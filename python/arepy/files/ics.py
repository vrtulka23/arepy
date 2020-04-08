import arepy as apy
import numpy as np

class ics:

    def __enter__(self):
        return self
        
    def __exit__(self, type, value, tb):
        return

    def __init__(self,units,density=None,**header):
        """Initial Conditions
        
        :param dict/int units: Dictionary with units or parameter file name
        :param callable/[float]/float density: Density function, list or a scalar in code units
        :param dict header: Additional header settings
        """
        
        apy.shell.printc('Creating initial conditions')

        self.header = {
            'NumPart_ThisFile':          [0]*6,
            'NumPart_Total':             [0]*6,
            'NumPart_Total_HighWord':    [0]*6,
            'MassTable':                 [0.0]*6,
            'Redshift':                  0.0,
            'BoxSize':                   1.0,  # in code units
            'Numfilespersnapshot':       1,
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
            'UnitLength_in_cm':          1,
            'UnitMass_in_g':             1,
            'UnitVelocity_in_cm_per_s':  1,
            'Time':                      0,
        }

        # set density
        self.density = density  # code units
        
        # set units and box size
        if isinstance(units,str):
            with apy.files.param(units) as f:
                params = f.getValue(['BoxSize', 'UnitMass_in_g', 'UnitLength_in_cm', 'UnitVelocity_in_cm_per_s'])
            self.header['BoxSize'] =                  params['BoxSize']
            self.header['UnitLength_in_cm'] =         params['UnitLength_in_cm']
            self.header['UnitMass_in_g'] =            params['UnitMass_in_g']
            self.header['UnitVelocity_in_cm_per_s'] = params['UnitVelocity_in_cm_per_s']
            self.units = apy.units({
                'mass':     self.header['UnitMass_in_g'],
                'length':   self.header['UnitLength_in_cm'],
                'velocity': self.header['UnitVelocity_in_cm_per_s'],
            })            
        else:
            self.units = units
            self.header['UnitLength_in_cm'] =         self.units['length']
            self.header['UnitMass_in_g'] =            self.units['mass']
            self.header['UnitVelocity_in_cm_per_s'] = self.units['velocity']

        # set additional headers
        self.header.update(header)

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

    # Set cell properties directly
    def setCells(self,coords,volumes):
        self.nGas =       len(coords)
        self.coords =     coords                     # code units
        self.volumes =    volumes                    # code units
        if callable(self.density):
            self.density = self.density(self.coords) # code units
        self.masses =     self.density * volumes     # code units
        self.velocities = np.zeros((self.nGas,3))    # code units
        self.ids =        np.arange(1,1+self.nGas,dtype=np.uint32)

        print('Units  length  ', self.units['length'],   'cm =',   self.units.guess('length',1) )
        print('       mass    ', self.units['mass'],     'g =',    self.units.guess('mass',1) )
        print('       velocity', self.units['velocity'], 'cm/s ~', self.units.guess('time',1) )
        print('Cells  num     ', self.nGas )
        stats=['min','mean','max','sum']
        print('      ', apy.data.stats('volumes',       self.volumes, stats) )
        print('      ', apy.data.stats('volumes cm^3',  self.volumes*self.units['volume'], stats) )
        print('      ', apy.data.stats('masses',        self.masses, stats) )
        print('      ', apy.data.stats('masses g',      self.masses*self.units['mass'], stats) )
        stats=['min','mean','max']
        print('      ', apy.data.stats('density',       self.density, stats) )
        print('      ', apy.data.stats('density g/cm^3',self.density*self.units['density'], stats) )
        print('      ', apy.data.stats('ndensH cm^-3',  self.density*self.units['density']/apy.const.m_p, stats) )
        stats=['min','max']
        print('      ', apy.data.stats('coords',        self.coords, stats) )
        print('      ', apy.data.stats('coords cm',     self.coords*self.units['length'], stats) )
        boxSize = self.header['BoxSize']
        boxMass = self.masses.sum()
        boxVol = boxSize**3
        boxDens = boxMass/boxVol
        print('Box    volume   %.03e = %.03e cm^3   = '%(boxVol, boxVol*self.units['volume']),
               self.units.guess('volume',boxVol))
        print('       mass     %.03e = %.03e g      = '%(boxMass, boxMass*self.units['mass']),
               self.units.guess('mass',boxMass))
        print('       density  %.03e = %.03e g/cm^3'%(boxDens, boxDens*self.units['density']))
        print('       size     %.03e = %.03e cm     = '%(boxSize, boxSize*self.units['length']),
               self.units.guess('length',boxSize))

    # Write ICs into the file
    def write(self,fileName,**opt):
        apy.shell.printc('Writing to: '+fileName)
        with apy.files.snap(fileName,fmode='w',**opt) as sf:                
            sf.setProperty('Coordinates',  self.coords)
            sf.setProperty('Masses',       self.masses)
            sf.setProperty('Velocities',   self.velocities)
            sf.setProperty('ParticleIDs',  self.ids)            
            self.header['NumPart_ThisFile'] = [self.nGas,0,0,0,0,0]
            self.header['NumPart_Total'] =    [self.nGas,0,0,0,0,0]
            sf.setHeader(self.header)
