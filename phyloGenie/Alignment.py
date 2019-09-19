from Bio.Align.Applications import MuscleCommandline
from io import StringIO
from Bio import AlignIO, SeqIO
import os


# perform multiple sequence alignment using MUSCLE and write the alignment to a fasta file
from phyloGenie_backend.settings import BASE_DIR, MEDIA_ROOT


class MuscleMSA:

    def align(self, infile):
        in_file = infile
        muscle_cline = MuscleCommandline(input=in_file)
        stdout, stderr = muscle_cline()  # execute the muscle command
        alignment = AlignIO.read(StringIO(stdout), "fasta")
        file_name = '{}_aligned.fasta'.format(os.path.splitext(in_file)[0])
        file_path = os.path.join(MEDIA_ROOT, file_name)   # write the alignment to a temporary file
        with open(file_path, 'w') as f:
            SeqIO.write(alignment, f, 'fasta')
        return file_name


