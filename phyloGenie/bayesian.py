from phyloGenie.MrBayes import MrBayesCommandline
from Bio import Phylo
import re

class BayesianTreeConstructor:

    def bayesian(self):
        f = open("batch.txt", "w+")

        seq = ['set autoclose=yes nowarn=yes\n', 'execute primates.nex\n', 'lset nst=6 rates=gamma\n',
               'mcmc ngen=10000 savebrlens=yes samplefreq=10 file=primates.nex1\n', 'mcmc file=primates_mcmc.nex\n',
               'sump burnin = 250\n', 'sumt burnin = 250\n', 'quit']

        f.writelines(seq)
        f.close()
        batch_file = "batch.txt"

        mrbayes_cline = MrBayesCommandline(execute=batch_file, log='log.txt', end='')
        # print(mrbayes_cline)

        stdout, stderr = mrbayes_cline()

        with open("primates.nex.con.tre", 'r', ) as file:  # file name
            article_text = file.read()
            article_text = re.sub(r'\[&prob=.*?\]:', ':', article_text)
            article_text = re.sub(r'\[&length_mean=.*?}\]', '', article_text)
            # print(article_text)

        with open("primates.nex.con.tre", 'w', ) as f:
            f.write(article_text)
            f.close()

        # tree = Phylo.read('primates.nex.con.tre', 'nexus')
        # print(tree)

        Phylo.convert('primates.nex.con.tre', 'nexus', 'final_tree_bayesian.newick', 'newick')
