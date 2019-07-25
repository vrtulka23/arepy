import time
class showLeap:
    def __init__(self,name):
        print(name,end="")
        self.itime = time.time()
        self.stime = time.time()
        self.etime = 0
    def show(self,name):
        ntime = time.time()
        self.etime = ntime - self.stime
        self.stime = ntime
        #print('%-12s'%name, self.etime)
    def end(self):
        print(' in %.3f s'%(time.time() - self.itime))        

# Keeping track of the module loading times

leap = showLeap('Loading external modules')
import numpy as np;              leap.show('numpy')
import h5py as hp;               leap.show('h5py')
import scipy as scp;             leap.show('scipy')
import matplotlib as mpl;        leap.show('matplotlib')
leap.end()

leap = showLeap('Loading arepy modules')
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
leap.end()

from os.path import expanduser
with open(expanduser("~")+'/.arepy/settings','r') as f:
    settings = {}
    for line in f.read().split('\n'):
        if line:
            p,v = line.split('=')
            settings[p] = v

