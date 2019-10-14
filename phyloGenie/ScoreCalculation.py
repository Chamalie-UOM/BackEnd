import os

from phyloGenie.MstatX import MstatxCommandline
from phyloGenie_backend.settings import BASE_DIR
from phyloGenie.data.aaindex import *

"""Example to use MstatX wrapper"""


class SimilarityScoreCalculator:
    def calculation(self, in_file, data_type, out_file):
        path = os.path.join(BASE_DIR, 'phyloGenie', 'mstatx')
        if data_type == 'AA':
            mat_path = "data/aaindex/HENS920102.mat"
        else:
            mat_path = "data/aaindex/DNA.mat"
        mstatx_cline = MstatxCommandline(path, input=in_file, output=out_file, globalSum=True, matrix=mat_path)

        # to get the global similarity score  of the alignment
        print(mstatx_cline)  # ./mstatx -i Protein.fasta -o Protein_output.txt -g

        stdout, stderr = mstatx_cline()
        print(stdout)

        # read result file and return global score
        # file_name = out_file + '.txt'
        f = open(out_file, "r")
        score = f.read()
        os.remove(out_file)

        return float(score[0:8])  # result up to 6 decimal places
