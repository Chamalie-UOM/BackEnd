from Bio.Align.Applications import MuscleCommandline
from io import StringIO
from Bio import AlignIO, SeqIO
import os


# perform multiple sequence alignment using MUSCLE and write the alignment to a fasta file

class MuscleMSA:

    def align(self, infile):
        in_file = infile
        muscle_cline = MuscleCommandline(input=in_file)
        stdout, stderr = muscle_cline()  # execute the muscle command
        alignment = AlignIO.read(StringIO(stdout), "fasta")

        out_file = '{}_aligned.fasta'.format(os.path.splitext(in_file)[0])  # write the alignment to a temporary file
        with open(out_file, 'w') as f:
            SeqIO.write(alignment, f, 'fasta')
        return out_file


# msa = MSA()
# output =msa.doAlignment("Acanthaster_planci_Gnomon.fasta")


