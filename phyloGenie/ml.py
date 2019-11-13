import os
import sys

from Bio import Alphabet
from Bio.Phylo.Applications import PhymlCommandline
from io import StringIO
from Bio import AlignIO, SeqIO
from Bio import SeqIO
from Bio.Alphabet import IUPAC


class MlTreeConstructor:
    '''def formatConversion(self, data_type, file):

        temp = "{}.phylip".format(os.path.splitext(file)[0])
        # file_Handler = open(temp, "wb")
        # file_Handler.write(byte_file.read())
        # file_Handler.close()

        if data_type == 'DNA':
            AlignIO.convert(file, "fasta", temp, "phylip", alphabet=Alphabet.generic_nucleotide)
        else:
            AlignIO.convert(file, "fasta", temp, "phylip", alphabet=Alphabet.generic_protein)
        return temp '''

    def converter(self, file, data_type):
        base = os.path.splitext(file)[0]
        if data_type == 'DNA':
            return SeqIO.convert(file, "fasta",
                                 base + ".phylip", "phylip",
                                 alphabet=IUPAC.ambiguous_dna)
        else:
            return SeqIO.convert(file, "fasta",
                                 base + ".phylip", "phylip",
                                 alphabet=Alphabet.generic_protein)

    def ml(self, data_type, input_file):

        self.converter(input_file, data_type)
        base = os.path.splitext(input_file)[0]
        data_file = base + '.phylip'
        if data_type == 'DNA':
            phyml_cline = PhymlCommandline(input=data_file)
        else:
            phyml_cline = PhymlCommandline(input=data_file, datatype='aa')

        stdout, stderr = phyml_cline()
        os.rename(base + '.phylip_phyml_tree.txt', base + '_ml.newick')  # tree file is generated
        stat_file = base + '.phylip_phyml_stats.txt'
        os.remove(data_file)
        os.remove(stat_file)

