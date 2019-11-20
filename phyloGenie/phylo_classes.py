import csv
import os
from subprocess import call

from Bio import AlignIO, SeqIO, Alphabet
from Bio.Alphabet import IUPAC

from phyloGenie.DistanceMatrixCalculatorGPU import DistanceCalculator_GPU
from phyloGenie.DistanceMatrixCalculatorSerial import DistanceCalculator
from phyloGenie.NJ_treeSerial import NJTree
from phyloGenie.NJ_treev2 import NJTree_Full_GPU
from phyloGenie.bayesian import BayesianTreeConstructor
from phyloGenie.ml import MlTreeConstructor
from phyloGenie_backend.settings import MEDIA_ROOT
from .upgma_serial import *
from .upgma_complete_gpu import *
from phyloGenie_backend import settings


class Recommendation(object):
    def __init__(self):
        self.noOfSeq = 0
        self.lengthOfSeq = 0
        self.typeOfSeq = ""
        self.score = 0
        self.recommendedAlgorithms = []
        self.DNA_thresh = 0.75
        self.AA_thresh = 0.25

    def readFeaturesFile(self, path):
        file0 = open(os.path.join(settings.BASE_DIR, path))
        readFile = csv.reader(file0, delimiter=',')
        # readFile = csv.reader(file, delimiter=',')
        # readFile = file.split(',')
        for featureSet in readFile:
            self.noOfSeq = int(featureSet[0])
            self.lengthOfSeq = int(featureSet[1])
            self.typeOfSeq = featureSet[2]
            self.score = float(featureSet[3])
        # print(noOfSeq, lengthOfSeq, typeOfSeq, score)
        return self.noOfSeq, self.lengthOfSeq, self.typeOfSeq, self.score

    def RecommendationOne(self):
        self.recommendedAlgorithms.append("Maximum Likelihood")

    def RecommendationTwo(self):
        self.recommendedAlgorithms.append("Maximum Likelihood")
        self.recommendedAlgorithms.append("NJ")
        self.recommendedAlgorithms.append("UPGMA")

    def RecommendationThree(self):
        self.recommendedAlgorithms.append("NJ")
        self.recommendedAlgorithms.append("UPGMA")

    def RecommendationFour(self):
        self.recommendedAlgorithms.append("Maximum Parsimony")

    def RecommendationFive(self):
        self.recommendedAlgorithms.append("Bayesian")

    def RecommendByScore(self, thresh, score):
        if score <= thresh:
            self.RecommendationOne()
        else:
            self.RecommendationTwo()

    def recommendation(self, noOfSeq, lengthOfSeq, typeOfSeq, score):

        if noOfSeq <= 25:
            if lengthOfSeq <= 500:
                if typeOfSeq == 'DNA':
                    if self.DNA_thresh <= score:
                        self.RecommendationThree()
                    else:
                        self.RecommendationFour()
                else:
                    if self.AA_thresh <= score:
                        self.RecommendationFour()
                    else:
                        self.RecommendationFive()
            else:
                if typeOfSeq == 'DNA':
                    self.RecommendationFour()
                else:
                    self.RecommendationFive()
        else:
            if lengthOfSeq <= 500:
                if typeOfSeq == 'DNA':
                    if self.DNA_thresh <= score:
                        self.RecommendationTwo()
                    else:
                        self.RecommendationOne()
                else:
                    if self.AA_thresh <= score:
                        self.RecommendationThree()
                    else:
                        self.RecommendationFive()
            else:
                if typeOfSeq == 'DNA':
                    self.RecommendationOne()
                else:
                    self.RecommendationFive()

        # algorithms = ', '.join(self.recommendedAlgorithms)
        # algo_dict = {'algorithms': algorithms}
        return self.recommendedAlgorithms


############################################## Class for running phylo
class TreeGenerator(object):

    # Call distance matrix calculation
    def calculate_distance_matrix(self, type, file, processor):  # distance matrix calculation
        if type == 'DNA':
            matrix_type = 'blastn'
        else:
            matrix_type = 'blosum62'
        # Call for paralleled implementation if Processor set to GPU
        if processor == 'CPU':
            calculator = DistanceCalculator(matrix_type)
        else:
            calculator = DistanceCalculator_GPU(matrix_type)
        aln = AlignIO.read(open(file), 'fasta')
        dm = calculator.get_distance(aln)
        return dm

    def run_algorithm(self, algo, dataset):

        # Take the dataset in to a temporary file for method input
        alignment = dataset.data.open(mode='rb')
        temp = "{}.fasta".format(os.path.splitext(str(dataset.data))[0])
        fileHandler = open(temp, "wb")
        fileHandler.write(alignment.read())
        fileHandler.close()

        # run UPGMA
        if algo == 'UPGMA':
            # Run UPGMA serial implementation when dataset has less than  200 taxa
            if dataset.size <= 50:
                distanceMatrix = DistanceCalculation()

                # Distance matrix calculation invocation
                dm = distanceMatrix.calculate_distance_matrix(dataset.type, temp)

                # Tree construction
                constructor = UpgmaTreeConstructor()
                tree = constructor.upgma(dm)

                # Remove temporary file
                os.remove(temp)

                # Write the tree to a newick file and save to database
                tree_name = "{}_upgma.nw".format(os.path.splitext(str(dataset.data))[0])
                file_path = os.path.join(MEDIA_ROOT, 'trees', tree_name)
                Phylo.write(tree, file_path, 'newick')
                dataset.tree = tree_name
                dataset.save()

                Phylo.draw_ascii(tree)
                tree_newick = open(file_path, "r")
                newick_string = tree_newick.read()
                newick_string = newick_string.rstrip('\n')
                return newick_string

            # Run GPU implementation of UPGMA if dataset  has more than 200 taxa
            elif (dataset.size > 50):
                # return "dataset larger than 200"
                distanceMatrix = FullGpuDistanceCalculation()

                # Distance matrix calculation invocation
                dm = distanceMatrix.full_gpu_calculate_distance_matrix(dataset.type, temp)

                # Tree construction
                constructor = FullGpuUpgmaTreeConstructor()
                tree = constructor.full_gpu_upgma(dm)
                tree_name = "{}_upgma_gpu.nw".format(os.path.splitext(str(dataset.data))[0])
                # Remove temporary file
                os.remove(temp)

                # Write the tree to a newick file and save to database

                file_path = os.path.join(MEDIA_ROOT, 'trees', tree_name)
                Phylo.write(tree, file_path, 'newick')
                dataset.tree = tree_name
                dataset.save()

                Phylo.draw_ascii(tree)
                tree_newick = open(file_path, "r")
                newick_string = tree_newick.read()
                newick_string = newick_string.rstrip('\n')
                return newick_string

        # run NJ
        elif algo == 'NJ':
            if dataset.size <= 50:
                processor_type = 'CPU'
                dis_matrix = self.calculate_distance_matrix(dataset.type, temp, processor_type)

                # NJ Tree Generation
                genNJ = NJTree()
                tree = genNJ.nj(dis_matrix)
                tree_name = "{}_nj.nw".format(os.path.splitext(str(dataset.data))[0])

                # Remove temporary file
                os.remove(temp)

                # Write the tree to a newick file and save to database
                file_path = os.path.join(MEDIA_ROOT, 'trees', tree_name)
                Phylo.write(tree, file_path, 'newick')
                dataset.tree = tree_name
                dataset.save()

                Phylo.draw_ascii(tree)
                tree_newick = open(file_path, "r")
                newick_string = tree_newick.read()
                newick_string = newick_string.strip('\\n')
                return newick_string

            # Run GPU implementation of NJ if dataset  has more than 200 taxa
            elif dataset.size > 50:
                # return "dataset larger than 200"
                processor_type = 'GPU'
                dis_matrix = self.calculate_distance_matrix(dataset.type, temp, processor_type)

                # NJ Tree Generation with GPU acceleration
                genNJ = NJTree_Full_GPU()
                tree = genNJ.nj_full_gpu(dis_matrix)
                tree_name = "{}_nj_gpu.nw".format(os.path.splitext(str(dataset.data))[0])
                # Remove temporary file
                os.remove(temp)

                # Write the tree to a newick file and save to database

                file_path = os.path.join(MEDIA_ROOT, 'trees', tree_name)
                Phylo.write(tree, file_path, 'newick')
                dataset.tree = tree_name
                dataset.save()

                Phylo.draw_ascii(tree)
                tree_newick = open(file_path, "r")
                newick_string = tree_newick.read()
                newick_string = newick_string.rstrip('\n')
                return newick_string

        # run maximum parsimony
        elif algo == 'Maximum Parsimony':
            if dataset.type == 'DNA':
                SeqIO.convert(temp, "fasta",
                              "infile", "phylip",
                              alphabet=IUPAC.ambiguous_dna)

                call("phyloGenie/dnapars_noop")
                tree_newick = open("outtree", "r")
                newick_string = tree_newick.read()
                tree_newick.close()

                tree_name = "{}_pars.nw".format(os.path.splitext(str(dataset.data))[0])
                file_path = os.path.join(MEDIA_ROOT, 'trees', tree_name)
                dataset.tree = tree_name
                dataset.save()
                os.rename('outtree', file_path)

                os.remove(temp)
                os.remove("infile")
                os.remove("outfile")

                return newick_string

            else:
                SeqIO.convert(temp, "fasta",
                              "infile", "phylip",
                              alphabet=Alphabet.generic_protein)

                call("phyloGenie/protpars_serial")
                tree_newick = open("outtree", "r")
                newick_string = tree_newick.read()
                tree_newick.close()

                tree_name = "{}_pars.nw".format(os.path.splitext(str(dataset.data))[0])
                file_path = os.path.join(MEDIA_ROOT, 'trees', tree_name)
                dataset.tree = tree_name
                dataset.save()
                os.rename('outtree', file_path)

                os.remove(temp)
                os.remove("infile")
                os.remove("outfile")

                return newick_string

        # run ML
        elif algo == 'Maximum Likelihood':
            # Run PhyML version

            constructor = MlTreeConstructor()
            constructor.ml(dataset.type, temp)

            tree_name = "{}_ml.nw".format(os.path.splitext(str(dataset.data))[0])
            tree_newick = open(tree_name, "r")
            newick_string = tree_newick.read()
            tree_newick.close()

            file_path = os.path.join(MEDIA_ROOT, 'trees', tree_name)
            dataset.tree = tree_name
            dataset.save()
            os.rename(tree_name, file_path)

            # Remove temporary file
            os.remove(temp)

            return newick_string

        elif algo == "Bayesian":

            constructor = BayesianTreeConstructor()
            constructor.bayesian(temp, dataset.type)

            tree_name = "{}_tree_bayesian.nw".format(os.path.splitext(str(dataset.data))[0])
            tree_newick = open(tree_name, "r")
            newick_string = tree_newick.read()
            tree_newick.close()

            file_path = os.path.join(MEDIA_ROOT, 'trees', tree_name)
            dataset.tree = tree_name
            dataset.save()
            os.rename(tree_name, file_path)

            # Remove temporary file
            os.remove(temp)
            os.remove('log.txt')

            return newick_string
