import arepy as apy
import numpy as np

class icsCoord:

    # Use cell properties from a carthesian grid
    def useGrid(self,res):
        apy.shell.printc('regular grid: %d**3'%res)
        grid = apy.coord.gridCube([res]*3,points='centers',scatter=0.3/res)
        coords = np.array(grid.coords,dtype=np.float64)*self.header['BoxSize']
        volumes = np.full(len(coords),(self.header['BoxSize']/res)**3,dtype=np.float64)
        if self.density is None:
            apy.shell.exit('Density has to be set while using Grid! (ics.py)')
        self.setCells(coords,volumes)

    # Use cell properties from a snapshot
    def useSnapshot(self,snap):
        apy.shell.printc('snapshot grid: '+snap.fileName)
        data = snap.getProperty(['Coordinates','Masses','Density'])
        convBoxSize = self.header['BoxSize'] / snap.getHeader('BoxSize')
        volumes = data['Masses'] / data['Density'] * convBoxSize**3
        data['Coordinates'] *= convBoxSize
        if self.density is None:
            self.density = data['Density']
        self.setCells(data['Coordinates'],volumes)
    
