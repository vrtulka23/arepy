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
    def __init__(self,name,vmin,vmax,logscale=False):
        self.cmap = getattr(cm, name)
        self.logscale = logscale
        if logscale:
            self.vmin = np.log10(vmin)
            self.vmax = np.log10(vmax)
        else: 
            self.vmin = vmin
            self.vmax = vmax

    def getColor(self,value,clip=True):
        if self.logscale:
            value = np.log10(value)
        if clip:
            value = np.clip(value,self.vmin,self.vmax)
        color = (value-self.vmin)/(self.vmax-self.vmin)
        return self.cmap(color)
