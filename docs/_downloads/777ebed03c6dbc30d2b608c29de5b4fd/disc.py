import arepy as apy
import numpy as np
from scripy.examples.plots.grids import grids

class disc(grids):

    def init(self):
        self.setFigure(1,1,1,srow=4,scol=4.2,show=True,fileFormat='png')

    def plot(self):

        lim = [-1000,1000]
        sp = self.fig.getSubplot(0,0,title='Disk grid',xlabel='x',ylabel='y',zlabel='z',
                                 xyz=True, xlim=lim, ylim=lim, zlim=lim)
        grid = apy.coord.gridDisc([30],extent=[0.1,1000])
        x,y,z = grid.coords.T
        sp.addScatter(x,y,z,s=1,marker='.')
