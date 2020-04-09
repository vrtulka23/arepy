import arepy as apy
import numpy as np
import matplotlib.cm as cm

def palette(name,num,reverse=False):
    if num<2:
        apy.shell.exit("Pallet cannot be created for only one color")
    colors = [getattr(cm, name)(s/float(num-1)) for s in range(num)]
    if reverse:
        colors.reverse()
    return colors

class colormap:
    def __init__(self,name,vmin=None,vmax=None,logscale=False):
        # colorblind palettes taken from 
        # https://davidmathlogic.com/colorblind/#%23648FFF-%23785EF0-%23DC267F-%23FE6100-%23FFB000
        self.cblind = {
            'IBM':[(100,143,255),(120,94,240),(220,38,127),(254,97,0),(255,176,0)],
            'Wong':[(0,0,0),(230,159,0),(86,180,233),(0,158,115),(240,228,66),(0,114,178),(213,94,0),(204,121,167)],
            'Tol':[(51,34,136),(17,119,51),(68,170,153),(136,204,238),(221,204,119),(204,102,119),(170,68,153),(136,34,85)],
        }
        self.name = name
        if name in list(self.cblind.keys()): 
            # colorblind palettes
            self.cmap = [(r/255,g/255,b/255) for (r,g,b) in self.cblind[name]]
            self.vmin = 0
            self.vmax = len(self.cblind[name])-1
            self.logscale = logscale
        else:
            # standard Matplotlib palettes
            self.cmap = getattr(cm, name)
            self.logscale = logscale
            if logscale:
                self.vmin = np.log10(vmin)
                self.vmax = np.log10(vmax)
            else: 
                self.vmin = vmin
                self.vmax = vmax

    def getList(self,num=None):
        if self.name in list(self.cblind.keys()): 
            return self.cmap
        else:
            return 'Need to implement'

    def getColor(self,value,clip=True):
        if self.logscale:
            value = np.log10(value)
        if clip:
            value = np.clip(value,self.vmin,self.vmax)
        if self.name in list(self.cblind.keys()): 
            return self.cmap[int(value)]
        else:
            color = (value-self.vmin)/(self.vmax-self.vmin)
            return self.cmap(color)
        
