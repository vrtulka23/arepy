import numpy as np
import arepy as apy
import h5py as hp

class propClass:

    def __init__(self,fileName,fmode,fnum,optChem,comoving):
        self.sf = hp.File(fileName,fmode)
        self.fileName = fileName
        self.fmode = fmode
        self.fnum = fnum

        self.comoving = comoving
        self.chem = optChem
        self.units = {
            'mass':     self.sf['Header'].attrs['UnitMass_in_g'],
            'length':   self.sf['Header'].attrs['UnitLength_in_cm'],
            'velocity': self.sf['Header'].attrs['UnitVelocity_in_cm_per_s'],
            'volume':   self.sf['Header'].attrs['UnitLength_in_cm']**3,
            'density':  self.sf['Header'].attrs['UnitMass_in_g']/self.sf['Header'].attrs['UnitLength_in_cm']**3,
            'energy':   self.sf['Header'].attrs['UnitVelocity_in_cm_per_s']**2 * self.sf['Header'].attrs['UnitMass_in_g'],
        }
        if 'Parameters' in self.sf:
            if 'UnitPhotons_per_s' in self.sf['Parameters'].attrs:
                self.units['flux'] = self.sf['Parameters'].attrs['UnitPhotons_per_s']

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.sf.close()

    ########################
    # Calculating properties
    ########################

    def hasProperty(self,prop):
        return hasattr(self,'prop_'+prop['name'])

    def getProperty(self,prop,ids=None,dictionary=False):
        properties = apy.files.properties(prop)
        for pp in properties:
            if ids is None:
                npart = self.sf['Header'].attrs['NumPart_ThisFile'][pp['ptype']]
                indexes = slice(0,npart)
            else:
                indexes = ids
            properties.setData( pp['key'], getattr(self,'prop_'+pp['name'])(pp,indexes) )
        return properties.getData(dictionary=dictionary)

    ##########################
    # Reading datasets from the snapshot
    ##########################

    def hasDataset(self,name,ptype):
        return True if name in self.sf['PartType%d'%ptype] else False

    def getDataset(self,name,ptype,ids,select=None):
        dset = self.sf['PartType%d/%s'%(ptype,name)]
        data = dset[:,select] if select is not None else dset[:]
        return data[ids]

            
