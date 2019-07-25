import numpy as np

class imgDim:
    def __init__(self,*args):
        self.dims = {}
        if args:
            self.add(*args)
    def __getitem__(self, key):
        return self.dims[key]
    def add(self,name,xlim,ylim,xbins,ybins):
        dims = {'xlim':xlim,'ylim':ylim,'xbins':xbins,'ybins':ybins}
        dims['bins'] = [
            np.linspace(xlim[0],xlim[1],xbins),
            np.linspace(ylim[0],ylim[1],ybins)
        ]
        dims['extent'] = [xlim[0],xlim[1],ylim[0],ylim[1]]
        self.dims[name] = dims
