
from Bio import AlignIO, SeqIO
import copy
import time
from Bio.Phylo import BaseTree
from Bio._py3k import zip, range

import numpy as np
import pycuda.autoinit
import pycuda.driver as drv
from pycuda.compiler import SourceModule
from phyloGenie.DistanceMatrixCalculatorGPU import DistanceCalculator_GPU


# perform multiple sequence alignment using MUSCLE and write the alignment to a fasta file

class FullGpuDistanceCalculation:

    def full_gpu_calculate_distance_matrix(self, type, file):
        in_file = file
        if type == 'DNA':
            matrix_type = 'blastn'
        else:
            matrix_type = 'blosum62'

        calculator = DistanceCalculator_GPU(matrix_type)
        alignment = AlignIO.read(in_file, "fasta")
        dm = calculator.get_distance(alignment)
        return dm


class FullGpuUpgmaTreeConstructor:

    def full_gpu_upgma(self, distance_matrix):

        # make a copy of the distance matrix to be used
        dm = copy.deepcopy(distance_matrix)

        dm_count = copy.deepcopy(dm)
        for i in range(1, len(dm_count)):
            for j in range(0, i):
                dm_count[i, j] = 1

        # init terminal clades
        clades = [BaseTree.Clade(None, name) for name in dm.names]

        # init minimum index
        min_i = 0
        min_j = 0
        inner_count = 0

        # GPU kernel to find the minimum index and minimum distance
        mod = SourceModule("""
         __global__ void findMin(double *dm, long long *index, double *local_min, int c, int l)
        {
            int k = threadIdx.y + blockIdx.y*blockDim.y;  
            double min_dist = dm[k*c];  
            int id = 0 ;               
            for(int i= k*c ; i< (k+1)*c; i++){
                if(i<l)
                {
                    if(min_dist >= dm[i])
                    {
                        min_dist = dm[i];
                        id = i;
                    }
                } 
            }
            local_min[k]=min_dist;
            index[k]= id;

        }""")

        while len(dm) > 1:
            # host array creation
            time_gpu_start = time.time()
            mat = dm.matrix
            dm_cpu = np.array(mat[1][:-1])
            for i in range(2, len(dm)):
                dm_cpu = np.append(dm_cpu, mat[i][:-1])

            combinations = int(((len(dm) - 1) * len(dm)) / 2)

            if combinations < 1024*256:
                block_size = int(round((len(dm))/2))
            elif combinations < 1024*1024:
                block_size = 512
            else:
                block_size = 1024

            local_count = int(round(combinations/block_size))
            if local_count < 1024:
                grid_size = 1
            else:
                grid_size = int(round(local_count/1024))+1

            index = np.zeros(block_size, dtype=int)
            min_val = np.zeros(block_size, dtype=float)

            local_min_array_gpu = drv.mem_alloc(dm_cpu.nbytes)
            local_index_gpu = drv.mem_alloc(index.nbytes)
            local_min_gpu = drv.mem_alloc(min_val.nbytes)

            drv.memcpy_htod(local_min_array_gpu, dm_cpu)
            drv.memcpy_htod(local_index_gpu, index)
            drv.memcpy_htod(local_min_gpu, min_val)
            func = mod.get_function("findMin")

            # start.record()
            func(local_min_array_gpu, local_index_gpu, local_min_gpu,  np.int32(local_count), np.int32(len(dm_cpu)),
                 block=(1, block_size, 1), grid =(1, grid_size, 1))

            # end.record()
            # end.synchronize()
            drv.memcpy_dtoh(min_val, local_min_gpu)
            drv.memcpy_dtoh(index, local_index_gpu)

            min_val_new = min_val
            min_val = min_val.tolist()

            local_min_gpu.free()
            local_index_gpu.free()

            min_dist = min(min_val)
            global_id = 0
            for i in range(len(min_val_new)):
                if min_dist == min_val_new[i]:
                    global_id = index[i]
                    break

            for i in range(1, len(distance_matrix)):
                if global_id == 0:
                    min_i = 1
                    min_j = 0
                    break
                else:
                    t_val = ((i+1)*(i+2))/2
                    if global_id < t_val:
                        min_i = i+1
                        min_j = global_id-(t_val - i-1)
                        break
                    elif global_id == t_val:
                        min_i = i+2
                        min_j = 0
                        break

            # create clade
            clade1 = clades[min_i]
            clade2 = clades[min_j]
            inner_count += 1
            inner_clade = BaseTree.Clade(None, "Inner" + str(inner_count))
            inner_clade.clades.append(clade1)
            inner_clade.clades.append(clade2)

            # assign branch length
            if clade1.is_terminal():
                clade1.branch_length = min_dist * 1.0 / 2
            else:
                clade1.branch_length = min_dist * \
                                       1.0 / 2 - self._height_of(clade1)

            if clade2.is_terminal():
                clade2.branch_length = min_dist * 1.0 / 2
            else:
                clade2.branch_length = min_dist * \
                                       1.0 / 2 - self._height_of(clade2)

            # update node list
            clades[min_j] = inner_clade
            del clades[min_i]

            # rebuild distance matrix,
            # set the distances of new node at the index of min_j

            for k in range(0, len(dm)):
                r = 0
                if k != min_i and k != min_j:
                    r = dm_count[min_i, k] + dm_count[min_j, k]
                    dm[min_j, k] = ((dm[min_i, k] * dm_count[min_i, k]) + (dm[min_j, k] * dm_count[min_j, k])) / r
                    dm_count[min_j, k] = r

            dm_count.names[min_j] = "Inner" + str(inner_count)
            del dm_count[min_i]

            dm.names[min_j] = "Inner" + str(inner_count)

            del dm[min_i]
            inner_clade.branch_length = 0
            del dm_cpu
        return BaseTree.Tree(inner_clade)

    def _height_of(self, clade):

        height = 0

        if clade.is_terminal():
            height = clade.branch_length
        else:
            for terminal in clade.get_terminals():
                path = clade.get_path(target=terminal)
                height = 0
                for value in path:
                    height = height + value.branch_length
        return height

# Phylo.draw_ascii(upgma_tree)
