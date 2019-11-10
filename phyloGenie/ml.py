import os
import sys

from Bio import Alphabet
from Bio.Phylo.Applications import PhymlCommandline
from io import StringIO
from Bio import AlignIO, SeqIO


class MlTreeConstructor:

    def formatConversion(self, data_type, file):

        temp = "{}.phylip".format(os.path.splitext(file)[0])
        # file_Handler = open(temp, "wb")
        # file_Handler.write(byte_file.read())
        # file_Handler.close()

        if data_type == 'DNA':
            AlignIO.convert(file, "fasta", temp, "phylip", alphabet=Alphabet.generic_nucleotide)
        else:
            AlignIO.convert(file, "fasta", temp, "phylip", alphabet=Alphabet.generic_protein)
        return temp

    def ml(self, data_type, input_file):

        data_file = self.formatConversion(data_type, input_file)  # phylip converted file
        if data_type == 'DNA':
            phyml_cline = PhymlCommandline(input=data_file)
        else:
            phyml_cline = PhymlCommandline(input=data_file, datatype='aa')

        stdout, stderr = phyml_cline()
