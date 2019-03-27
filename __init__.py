import arepy.constants as const
from   arepy.units import *
import arepy.shell
import arepy.files
import arepy.plot
import arepy.util
import arepy.coord
import arepy.phys
import arepy.scripy
import arepy.data

from os.path import expanduser
with open(expanduser("~")+'/.arepy/settings','r') as f:
    settings = {}
    for line in f.read().split('\n'):
        if line:
            p,v = line.split('=')
            settings[p] = v
