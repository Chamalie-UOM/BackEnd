"""Command line wrapper for the Mstatx"""

from __future__ import print_function

from Bio.Application import _Option, _Switch, AbstractCommandline

"""Available options
    -a, --trident_a : Factor applied to t(x) (see trident) [default=1.0]
   -b, --trident_b : Factor applied to r(x) (see trident) [default=0.5]
   -c, --trident_c : Factor applied to g(x) (see trident) [default=3.0]
   -g, --global    : Output the global score                           
   -h, --help      : Print this help                                   
   -i, --input     : MSA input file name                               
   -m, --matrix    : Score matrix file name                            
   -n, --nb_seq    : Maximum number of sequences read [default=500]    
   -o, --output    : Output file name [default=ouput.txt]              
   -s, --statistic : Statistics [default=wentropy]                     
   -t, --threshold : Threshold to print correlation [default=0.8]      
   -v, --verbose   : Verbose mode                                      
   -w, --window    : Number of side columns (jensen score)  

    Available Statistics
  	wentropy (1)
  	trident  (1)
  	mvector  (1)
  	jensen   (1)
  	kabat    (1)
  	gap      (1)  """


class MstatxCommandline(AbstractCommandline):

    def __init__(self, cmd="./mstatx", **kwargs):
        STATISTICS = ["wentropy", "trident", "mvector", "jensen", "kabat", "gap"]
        self.parameters = [
            _Option(["-i", "i", "input"],
                    "--input is needed",
                    filename=True,
                    is_required=True,
                    equate=False),
            _Option(["-o", "output"],
                    "Output file name",
                    filename=True,
                    is_required=False,
                    equate=False),
            _Option(["-m", "matrix"],
                    "Score Matrix File name",
                    filename=True,
                    equate=False),
            _Option(["-s", "stat"],
                    "Statistics",  # default= Wentropy
                    checker_function=lambda x: x in STATISTICS,
                    equate=False),
            _Option(["-n", "nb"],
                    "nb_seq - Maximum number of sequences read",  # default= 500
                    checker_function=lambda x: isinstance(x, int),
                    equate=False),
            _Option(["-t", "t"],
                    "threashold -Threshold to print correlation",  # default= 0.8
                    checker_function=lambda x: isinstance(x, float),
                    equate=False),
            _Option(["-a", "a"],
                    "trident_a -Factor applied to t(x) (see trident)",  # default= 1.0
                    checker_function=lambda x: isinstance(x, float),
                    equate=False),
            _Option(["-b", "b"],
                    "trident_b -Factor applied to r(x) (see trident)",  # default= 0.5
                    checker_function=lambda x: isinstance(x, float),
                    equate=False),
            _Option(["-c", "c"],
                    "trident_c -Factor applied to g(x) (see trident)",  # default= 3.0
                    checker_function=lambda x: isinstance(x, float),
                    equate=False),
            _Option(["-w", "w"],
                    "window- Number of side columns (jensen score)",  # default= 3
                    checker_function=lambda x: isinstance(x, int),
                    equate=False),
            _Switch(["-g", "globalSum"],
                    "Output the global score"),  # default=false
            _Switch(["-v", "verbose"],
                    "Verbose mode"),  # default=false
            _Switch(["-h", "help"],
                    "Print this help"),  # default=false
        ]

        AbstractCommandline.__init__(self, cmd, **kwargs)
