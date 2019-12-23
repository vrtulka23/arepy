import numpy as np
import arepy as apy
import h5py as hp

class main:

    def __init__(self,opt):
        # Update default options
        self.opt = {
            'sinkOpt':  None,
            'snapFile': None,
            'snapMode': 'r',
            'comoving': False,
            'chem':     'sgchem1',
            **opt
        }

        self.fileSnap = hp.File(self.opt['snapFile'],self.opt['snapMode'])
        self.fileSink = None

        self.snapTime = self.fileSnap['Header'].attrs['Time']
        
        self.units = {
            'mass':     self.fileSnap['Header'].attrs['UnitMass_in_g'],
            'length':   self.fileSnap['Header'].attrs['UnitLength_in_cm'],
            'velocity': self.fileSnap['Header'].attrs['UnitVelocity_in_cm_per_s'],
            'volume':   self.fileSnap['Header'].attrs['UnitLength_in_cm']**3,
            'density':  self.fileSnap['Header'].attrs['UnitMass_in_g']/self.fileSnap['Header'].attrs['UnitLength_in_cm']**3,
            'energy':   self.fileSnap['Header'].attrs['UnitVelocity_in_cm_per_s']**2 * self.fileSnap['Header'].attrs['UnitMass_in_g'],
        }

        if 'Parameters' in self.fileSnap:
            if 'UnitPhotons_per_s' in self.fileSnap['Parameters'].attrs:
                self.units['flux'] = self.fileSnap['Parameters'].attrs['UnitPhotons_per_s']

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.fileSnap.close()

    ########################
    # Calculating properties
    ########################

    def hasProperty(self,prop):
        return hasattr(self,'prop_'+prop['name'])

    def getProperty(self,prop,ids=None,ptype=0,dictionary=False):
        properties = apy.files.properties(prop,ptype=ptype)
        for pp in properties:
            npart = self.fileSnap['Header'].attrs['NumPart_ThisFile'][pp['ptype']]
            propMethod = 'prop_'+pp['name']
            if not hasattr(self,propMethod):
                properties.setData( pp['key'], [] )
                apy.shell.warn("Property '%s' it is not defined! (propClass)"%pp['name'])
            elif npart>0:
                indexes = slice(0,npart) if ids is None else ids
                properties.setData( pp['key'], getattr(self,propMethod)(indexes,**pp) )
            else:
                properties.setData( pp['key'], [] )
        return properties.getData(dictionary=dictionary)

    ################################
    # Reading data from the snapshot
    ################################

    def hasSnapData(self,name,ptype):
        return True if name in self.fileSnap['PartType%d'%ptype] else False

    def getSnapData(self,name,ptype,ids,select=None):
        dset = 'PartType%d/%s'%(ptype,name)
        if dset in self.fileSnap:
            dset = self.fileSnap[dset]
            data = dset[:,select] if select is not None else dset[:]
            return data[ids]
        else:
            apy.shell.warn("Dataset '%s' was not found in file '%s'! (propClass.py)"%(dset,self.opt['snapFile']))
            return np.nan

    ###############################
    # Reading from a sink snapshot
    ###############################

    def getSinkData(self,name,ids):
        if self.fileSink is None:
            # open the sink file and cross-match ids
            self.fileSink = apy.files.sink(**self.opt['sinkOpt'])
            snapIds = self.getSnapData('ParticleIDs',5,ids)
            sinkIds = self.fileSink.getValues('ID')
            self.idsSink = np.nonzero(snapIds[:, None] == sinkIds)[1]
        return self.fileSink.getValues(name)[self.idsSink]
