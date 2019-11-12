import glob
import os

from Bio.Alphabet import IUPAC
from Bio import Alphabet
from phyloGenie.MrBayes import MrBayesCommandline
from Bio import Phylo, SeqIO
import re

class BayesianTreeConstructor:

    def converter(self, file, data_type):
        base = os.path.splitext(file)[0]
        if data_type == 'DNA':
            return SeqIO.convert(file, "fasta",
                                 base + ".nex", "nexus",
                                 alphabet=IUPAC.ambiguous_dna)
        else:
            return SeqIO.convert(file, "fasta",
                                 base + ".nex", "nexus",
                                 alphabet=Alphabet.generic_protein)

    def bayesian(self, file_name, data_type):

        nex_file = self.converter(file_name, data_type)
        base = os.path.splitext(nex_file)[0]
        bat_file = base + '_batch.txt'
        f = open(bat_file, "w+")

        seq = ['set autoclose=yes nowarn=yes\n', 'execute ' + base + '.nex\n', 'lset nst=6 rates=gamma\n',
               'mcmc ngen=10000 savebrlens=no samplefreq=10\n',
               'sump burnin = 250\n', 'sumt burnin = 250\n', 'quit']

        f.writelines(seq)
        f.close()

        batch_file = bat_file
        # start_time = time.time()
        mrbayes_cline = MrBayesCommandline(execute=batch_file, log='log.txt', end='')
        # print(mrbayes_cline)

        stdout, stderr = mrbayes_cline()
        # end_time = time.time()

        # print('time taken', (end_time - start_time))
        os.remove(bat_file)
        os.rename(base + '.nex.con.tre', base + '_tree.nexus')
        for filename in glob.glob(base + '.nex.*'):
            os.remove(filename)

        tree_file = base + '_tree.nexus'

        with open(tree_file, 'r', ) as file:  # file name
            article_text = file.read()
            article_text = re.sub(r'\[&prob=.*?\]:', ':', article_text)
            article_text = re.sub(r'\[&length_mean=.*?}\]', '', article_text)
        # print(article_text)

        with open(tree_file, 'w', ) as f:
            f.write(article_text)
            f.close()

        tree_base = os.path.splitext(tree_file)[0]

        Phylo.convert(tree_file, 'nexus', tree_base + '.newick', 'newick')
        os.remove(tree_file)


