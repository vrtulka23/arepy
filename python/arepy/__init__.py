"""Python module ArePy

ArePy is an open-source Analyzing tool for Arepo simulation data. 
The main module is written in Python, but some parts are also written in bash.

.. moduleauthor:: Ondrej Jaura

"""

import yaml
from arepy.showLeap import *
from arepy.config import config
    
# Keeping track of the module loading times

with showLeap('Loading external modules') as leap:
    import numpy as np;              leap.show('numpy')
    import h5py as hp;               leap.show('h5py')
    import scipy as scp;             leap.show('scipy')
    import matplotlib as mpl;        leap.show('matplotlib')
    import multiprocessing as mpi;   leap.show('multiprocessing')

with showLeap('Loading arepy modules') as leap:
    import arepy.constants as const; leap.show('const')
    from   arepy.units import *;     leap.show('units')
    import arepy.shell;              leap.show('shell')
    import arepy.data;               leap.show('data')
    import arepy.files;              leap.show('files')
    import arepy.plot;               leap.show('plot')   # this module takes more time because of the pyplot
    import arepy.util;               leap.show('util')
    import arepy.coord;              leap.show('coord')
    import arepy.phys;               leap.show('phys')
    import arepy.scripy;             leap.show('scripy')

from os.path import dirname,realpath,expanduser
dirHome = expanduser("~")
dirModule = dirname(dirname(dirname(realpath(__file__))))
dirArepy = dirModule+'/python/arepy'
dirScripy = dirModule+'/python/scripy'
dirResults = dirModule+'/results'
fileConfig = dirHome+"/.arepy"

def readConfigFile(filename):
    if arepy.shell.isfile(filename):
        with open(filename, "r") as f:
            configFromFile = yaml.load(f)
            config.update(configFromFile)

readConfigFile(fileConfig)

numCpu = mpi.cpu_count()
