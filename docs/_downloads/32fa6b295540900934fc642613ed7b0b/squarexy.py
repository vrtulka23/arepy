import arepy as apy
import numpy as np
from scripy.examples.plots.grids import grids

class squarexy(grids):

    def init(self):
        self.setFigure(1,1,1,srow=4,scol=4,show=True,fileFormat='png')

    def plot(self):

        lim = [-1000,1000]
        sp = self.fig.getSubplot(0,0,title='Square grid',xlabel='x',ylabel='y',zlabel='z',
                                 xyz=True, xlim=lim, ylim=lim, zlim=lim)
        extent = [-900,900,-900,900]
        grid = apy.coord.gridSquareXY([40,40],extent=extent,zfill=0)
        x,y,z = grid.coords.T
        sp.addScatter(x,y,z,s=1,marker='.')
