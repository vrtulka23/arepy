import arepy as apy
import numpy as np

class ics:

    def __enter__(self):
        return self
        
    def __exit__(self, type, value, tb):
        return

    def __init__(self,units,**nopt):

        apy.shell.printc('Creating initial conditions')

        self.opt = {
            'Redshift':             0.0,
            'BoxSize':              1.0,
            'NumFilesPerSnapshot':  1,
        }
        self.opt.update(nopt)
        self.units = units

    # Use cell properties from a carthesian grid
    def useGrid(self,res,density):
        apy.shell.printc('regular grid: %d**3'%res)
        grid,xi = apy.coord.gridCube([res]*3,points='centers',scatter=0.3/res)
        coords = np.array(grid,dtype=np.float64)*self.opt['BoxSize']
        volumes = np.full(len(coords),(self.opt['BoxSize']/res)**3,dtype=np.float64)
        self.setCells(coords,volumes,density)

    # Use cell properties from a snapshot
    def useSnapshot(self,snap,density):
        apy.shell.printc('snapshot grid: '+snap.fileSnap)
        coords, masses, dens = snap.getProperty(['Coordinates','Masses','Density'])
        convBoxSize = self.opt['BoxSize'] / snap.getHeader('BoxSize')
        volumes = masses/dens * convBoxSize**3
        coords *= convBoxSize
        self.setCells(coords,volumes,density)

    # Set cell properties directly
    def setCells(self,coords,volumes,density):
        self.nGas =       len(coords)
        self.coords =     coords
        self.volumes =    volumes
        self.density =    density if np.isscalar(density) else density(self.coords)
        self.masses =     self.density * volumes
        self.velocities = np.zeros((self.nGas,3))
        self.ids =        np.arange(1,1+self.nGas,dtype=np.uint32)

        print( 'Units  length  ', self.units['length'], 'cm =', self.units.guess('length',1) )
        print( '       mass    ', self.units['mass'], 'g =', self.units.guess('mass',1) )
        print( '       velocity', self.units['velocity'], 'cm/s ~', self.units.guess('time',1) )
        print( 'Cells  num     ', self.nGas )
        print( '       vol     ', apy.data.stats(self.volumes,['min','mean','max','sum']) )
        print( '       masses  ', apy.data.stats(self.masses,['min','mean','max','sum']))
        print( '       dens    ', apy.data.stats(self.density,['min','mean','max']))
        print( '       coord   ', apy.data.stats(self.coords,['min','max']))
        boxSize = self.opt['BoxSize']
        boxMass = self.masses.sum()
        boxDens = boxMass/boxSize**3
        print( 'Box    size     %.03e = %.03e cm     ='%(boxSize, boxSize*self.units['length']), )
        print( self.units.guess('length',boxSize))
        print( '       mass     %.03e = %.03e g      ='%(boxMass, boxMass*self.units['mass']),)
        print( self.units.guess('mass',boxMass))
        print( '       volume   %.03e = %.03e cm^3'%(boxSize**3, boxSize**3 * self.units['volume']))
        print( '       dens     %.03e = %.03e g/cm^3'%(boxDens, boxDens*self.units['density']))

    # Write ICs into the file
    def write(self,fileName,**opt):
        apy.shell.printc('Writing to: '+fileName)
        with apy.files.snap(fileName,fmode='w',**opt) as sf:                
            sf.setProperty(0,'Coordinates',  self.coords)
            sf.setProperty(0,'Masses',       self.masses)
            sf.setProperty(0,'Velocities',   self.velocities)
            sf.setProperty(0,'ParticleIDs',  self.ids)            
            sf.setHeader({
                'NumPart_ThisFile':          [self.nGas,0,0,0,0,0],
                'NumPart_Total':             [self.nGas,0,0,0,0,0],
                'NumPart_Total_HighWord':    [0]*6,
                'MassTable':                 [0.0]*6,
                'Redshift':                  self.opt['Redshift'],
                'BoxSize':                   self.opt['BoxSize'],
                'NumFilesPerSnapshot':       self.opt['NumFilesPerSnapshot'],
                'Omega0':                    0.0,
                'OmegaLambda':               0.0,
                'OmegaBaryon':               0.0,
                'HubbleParam':               1.0,
                'Flag_Sfr':                  0,
                'Flag_Cooling':              0,
                'Flag_StellarAge':           0,
                'Flag_Metals':               0,
                'Flag_Feedback':             0,
                'Flag_DoublePrecision':      1,
                'Composition_vector_length': 0,
                'UnitLength_in_cm':          self.units['length'],
                'UnitMass_in_g':             self.units['mass'],
                'UnitVelocity_in_cm_per_s':  self.units['velocity'],
                'Time':0
            })
