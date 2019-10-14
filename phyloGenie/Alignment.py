import sys
import os


# perform multiple sequence alignment using MUSCLE and write the alignment to a fasta file
from phyloGenie.Muscle import MuscleCommandline
from io import StringIO
from Bio import AlignIO, SeqIO
from phyloGenie_backend.settings import MEDIA_ROOT, BASE_DIR


class MuscleMSA:
    no_of_taxa = 0
    seq_len = 0

    def align(self, infile):
        in_file = infile
        path = os.path.join(BASE_DIR, 'phyloGenie', 'muscle')
        print(path)

        muscle_cline = MuscleCommandline(path, input=in_file)
        stdout, stderr = muscle_cline()  # execute the muscle command
        # check the python version
        if sys.version_info[0] < 3:
            stdout = stdout.decode("utf-8", 'ignore')

        alignment = AlignIO.read(StringIO(stdout), "fasta")

        self.no_of_taxa = len(alignment)
        self.seq_len = len(alignment[0].seq)
        return alignment, self.no_of_taxa, self.seq_len

    def writeAlignmentFile(self, alignment, in_file):
        file_name = '{}_aligned.fasta'.format(os.path.splitext(in_file)[0])
        file_path = os.path.join(MEDIA_ROOT, file_name)   # write the alignment to a temporary file
        with open(file_path, 'w') as f:
            SeqIO.write(alignment, f, 'fasta')
        return file_name
