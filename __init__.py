import arepy.constants as const
import arepy.shell as shell
import arepy.files
import arepy.plot
import arepy.util
import arepy.coord
from   arepy.units import *
import arepy.phys
import arepy.scripy
import arepy.data

from os.path import expanduser
with open(expanduser("~")+'/.bitsandpieces/settings','r') as f:
    settings = {}
    for line in f.read().split('\n'):
        p,v = line.split('=')
        settings[p] = v
