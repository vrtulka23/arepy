import arepy as apy
import numpy as np

from arepy.files.icsGrid import *
from arepy.files.icsVelocity import *

class ics(icsGrid,icsVelocity):

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
            'NumFilesPerSnapshot':       1,
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
            print('Parameters set from: '+units)
            with apy.files.param(units) as f:
                params = f.getValue([
                    'BoxSize', 'UnitMass_in_g', 'UnitLength_in_cm', 'UnitVelocity_in_cm_per_s',
                    'ReferenceGasPartMass'
                ])
            self.header['BoxSize'] =                  params['BoxSize']
            self.header['UnitLength_in_cm'] =         params['UnitLength_in_cm']
            self.header['UnitMass_in_g'] =            params['UnitMass_in_g']
            self.header['UnitVelocity_in_cm_per_s'] = params['UnitVelocity_in_cm_per_s']
            self.units = apy.units({
                'mass':     self.header['UnitMass_in_g'],
                'length':   self.header['UnitLength_in_cm'],
                'velocity': self.header['UnitVelocity_in_cm_per_s'],
            })
            self.other = {
                'ReferenceGasPartMass': params['ReferenceGasPartMass']
            }
        else:
            print('Parameters set by hand')
            self.units = units
            self.header['UnitLength_in_cm'] =         self.units['length']
            self.header['UnitMass_in_g'] =            self.units['mass']
            self.header['UnitVelocity_in_cm_per_s'] = self.units['velocity']
            self.other = {}

        # set additional headers before prints
        self.header.update(header)

        print('Units  length  ', self.units['length'],   'cm =',   self.units.guess('length',1) )
        print('       mass    ', self.units['mass'],     'g =',    self.units.guess('mass',1) )
        print('       velocity', self.units['velocity'], 'cm/s ~', self.units.guess('time',1) )
        boxSize = self.header['BoxSize']
        boxVol = boxSize**3
        print('Box    size     %.03e = %.03e cm     = '%(boxSize, boxSize*self.units['length']),
               self.units.guess('length',boxSize))
        print('       volume   %.03e = %.03e cm^3   = '%(boxVol, boxVol*self.units['volume']),
               self.units.guess('volume',boxVol))
        if 'ReferenceGasPartMass' in self.other:
            rmass = self.other['ReferenceGasPartMass']
            print('Other:')
            print('ReferenceGasPartMass  %.03e = %.03e g = '%(rmass,rmass*self.units['mass']),
                  self.units.guess('mass',rmass) )

    # Write ICs into the file
    def write(self,fileName,**opt):
        apy.shell.printc('Writing to: '+fileName)
        with apy.files.snap(fileName,fmode='w',**opt) as sf:                
            sf.setProperty('Coordinates',  self.coords)
            sf.setProperty('Masses',       self.masses)
            sf.setProperty('Velocities',   self.velocities)
            sf.setProperty('ParticleIDs',  self.ids)            
            self.header['NumPart_ThisFile'] = self.npart
            self.header['NumPart_Total'] =    self.npart
            sf.setHeader(self.header)

        print('Cells  num     ', self.npart )
        stats=['min','mean','max','sum']
        print('      ', apy.data.stats('volumes',       self.volumes, stats) )
        print('      ', apy.data.stats('volumes cm^3',  self.volumes*self.units['volume'], stats) )
        print('      ', apy.data.stats('masses',        self.masses, stats) )
        print('      ', apy.data.stats('masses g',      self.masses*self.units['mass'], stats) )
        stats=['min','mean','max']
        print('      ', apy.data.stats('density',       self.density, stats) )
        print('      ', apy.data.stats('density g/cm^3',self.density*self.units['density'], stats) )
        print('      ', apy.data.stats('ndensH cm^-3',  self.density*self.units['density']/apy.const.m_p, stats) )
        stats=['min','mean','max']
        print('      ', apy.data.stats('coords',        self.coords, stats) )
        print('      ', apy.data.stats('coords cm',     self.coords*self.units['length'], stats) )
        print('      ', apy.data.stats('velocity',      self.velocities, stats) )
        print('      ', apy.data.stats('velocity cm/s', self.velocities*self.units['velocity'], stats) )
        boxMass = self.masses.sum()
        boxVol = self.header['BoxSize']**3
        boxDens = boxMass/boxVol
        print('Box    mass     %.03e = %.03e g      = '%(boxMass, boxMass*self.units['mass']),
               self.units.guess('mass',boxMass))
        print('       density  %.03e = %.03e g/cm^3'%(boxDens, boxDens*self.units['density']))
