from Bio import AlignIO, SeqIO
from Bio import Phylo
from Bio.Phylo.TreeConstruction import DistanceCalculator
import copy
import time
from Bio.Phylo import BaseTree
from Bio._py3k import zip, range
import numpy as np


# perform multiple sequence alignment using MUSCLE and write the alignment to a fasta file

class DistanceCalculation:

    def calculate_distance_matrix(self, type, file):
        in_file = file
        # print(type(in_file))
        if type == 'DNA':
            matrix_type = 'blastn'
        else:
            matrix_type = 'blosum62'

        calculator = DistanceCalculator(matrix_type)
        alignment = AlignIO.read(in_file, "fasta")
        dm = calculator.get_distance(alignment)
        return dm


class UpgmaTreeConstructor:
    gap = 0
    def upgma(self, distance_matrix):

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

        while len(dm) > 1:
            min_dist = dm[1, 0]
            # find minimum index

            mintime = time.time()
            for i in range(1, len(dm)):
                for j in range(0, i):
                    if min_dist >= dm[i, j]:
                        min_dist = dm[i, j]
                        min_i = i
                        min_j = j

            mintime2 = time.time()

            self.gap += mintime2 - mintime

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



