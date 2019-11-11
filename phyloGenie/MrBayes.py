"""Command line wrapper for the MrBayes"""

from __future__ import print_function

from Bio.Application import _Option, _Switch, AbstractCommandline


class MrBayesCommandline(AbstractCommandline):

    def __init__(self, cmd="mb", **kwargs):
        self.parameters = [
            _Option(['-i', '--input', 'input'],
                    "PHYLIP format input nucleotide or amino-acid sequence filename.",
                    filename=True,
                    is_required=False,
                    equate=True,
                    ),
            _Option(['<', '-execute', 'execute'],
                    "to execute batch text",
                    filename=True,
                    is_required=True,
                    equate=False,
                    ),
            _Option(['>', '--log', 'log'],
                    "log file.",
                    filename=True,
                    is_required=True,
                    equate=False,
                    ),
            _Option(['&', '--&', 'end'],
                    "command end",
                    filename=False,
                    is_required=True,
                    equate=False,
                    ),
        ]
        AbstractCommandline.__init__(self, cmd, **kwargs)
