import numpy as np
import h5py as hp
import arepy as apy
import os

# Property list
from arepy.files.properties import *    # Property list class

# Snapshot properties
from arepy.files.propClass import *     # Parent class for simple properties
from arepy.files.propSimple import *    # Simple properties
from arepy.files.propSgchem1 import *   # SGChem specific properties
from arepy.files.propComplex import *   # Complex properties
from arepy.files.propSink import *      # Properties from a sink file

# Property glues
from arepy.files.glueClass import *     # Parent class for property glues
from arepy.files.glueSimple import *    # Simple property glues

# Snapshot class
class snap(propComplex):
    def __enter__(self):
        return self
    def __exit__(self, type, value, tb):
        return
    def __init__(self,fileName,**opt):
        # set options
        self.opt = {
            'fmode':    'r',
            'nsub':     1,
            'nproc':    1,
            'initChem': 'sgchem1',
            'comoving': False,
            'snapFile': fileName,
            'sinkOpt':  None,
            # other: nproc, nproc_ckdt
            **opt
        }

        # initial parameters
        self.fileName = fileName
            
        # initialize chemistry
        self.initChem(self.opt['initChem'])
        
        # parse all file names
        if self.opt['nsub']>1:
            self.sfileName = [ self.fileName%f for f in range(self.opt['nsub']) ]
        else:
            self.sfileName = [ self.fileName ]

        for f in self.sfileName:
            if not os.path.isfile(f):
                if self.opt['fmode']=='w':
                    apy.shell.prompt('Following file was not found! (snap.py)\n%s\nDo you want to create new?'%f)
                    hp.File(f,'w')
                else:
                    apy.shell.warn("Following file was not found! (snap.py)\n%s"%f)

    def initChem(self,opt):
        if isinstance(opt,dict):
            self.optChem = opt.copy()
        elif isinstance(opt,str):
            self.optChem = {'type':opt}
        else:
            apy.shell.exit('Chemistry has to be initialized (snap.py)')
        if self.optChem['type']=='sgchem1':
            if 'abund' in self.optChem:
                if self.optChem['abund']=='HydrogenOnly':
                    self.optChem.update({'X_H':1.,'x0_H':1.,'x0_He':0.,'x0_D':0.})
                elif isinstance(self.optChem['abund'],dict):
                    self.optChem.update(self.optChem['abund'])
            else:
                self.optChem.update({'X_H':0.76,'x0_H':1.,'x0_He':0.079,'x0_D':2.6e-5})
                
    def delDataset(self,dset):
        for sfileName in self.sfileName:
            with hp.File(sfileName,self.opt['fmode']) as f:
                if dset in f:
                    del f[dset]

    def _setHeader(self,name,value,s=0):
        with hp.File(self.sfileName[s],'r+') as f:
            if 'Header' not in f:
                f.create_group('Header')
            if name in f['Header'].attrs:
                f['Header'].attrs[name] = value
            else:
                f['Header'].attrs.create(name,value)
    def setHeader(self,name,value=None,s=0):
        if isinstance(name,dict):
            for n,v in name.items():
                self._setHeader(n,v,s=s)
        else:
            self._setHeader(name,value,s=s)


    def getHeader(self,names=None,s=0):
        if names is None:
            with hp.File(self.sfileName[s],self.opt['fmode']) as f:
                return dict(f['Header'].attrs)
        else:
            allNames = [names] if isinstance(names,str) else names
            with hp.File(self.sfileName[s],self.opt['fmode']) as f:
                data = {}
                nameStd = ['NumPart_Total','NumPart_ThisFile','HubbleParam','Time','BoxSize']
                for name in allNames:
                    if name in nameStd:
                        data[name] = f['Header'].attrs[name]
                    else:
                        data[name] = getattr(apy.files,self.optChem['type']).getHeader(f,name)
            if isinstance(names,str):
                return list(data.values())[0] 
            else:
                return {name:data[name] for name in allNames}

    def getUnits(self,newUnits=None,comoving=False):
        names = ['UnitMass_in_g','UnitLength_in_cm','UnitVelocity_in_cm_per_s']
        if self.opt['comoving'] or comoving:
            names += ['HubbleParam','ExpansionFactor']
        values = self.getHeader(names)
        units = {'mass':values[0],'length':values[1],'velocity':values[2]}
        if self.opt['comoving'] or comoving:
            units['h'] = values[3]
            units['a'] = values[4]
        return apy.units(oldUnits=units,newUnits=newUnits)

    def setProperty(self,ptype,name,data,ids=None,s=0):
        fileName = self.sfileName[s]
        with hp.File(fileName,'r+') as f:
            pt = 'PartType%d'%ptype
            if pt not in f:
                f.create_group(pt)
            if name not in f[pt]:
                f[pt].create_dataset(name,data=data)
            if ids:
                f[pt][name][ids] = data
            else:
                if f[pt][name].shape!=data.shape:
                    apy.shell.prompt('%s have wrong shape! Change the original shape?'%name)
                    del f[pt][name]
                    f[pt].create_dataset(name,data=data)
                else:
                    f[pt][name][:] = data

    def listProperties(self,ptype,s=0):
        with hp.File(self.sfileName[s],self.opt['fmode']) as f:
            pt = 'PartType%d'%ptype
            return f[pt].keys()

    #########################
    # Properties
    #########################

    # This function switches between complex and simple properties
    # Example: sn.getProperty(['Masses',{'name':'Minimum','p':'PosX'}])
    def getProperty(self,props,ids=None,ptype=None,dictionary=False):
        # Convert to array if needed
        aProps = apy.files.properties(props,ptype=ptype)

        # Select and load simple properties
        sProps = aProps.getSimple()
        if sProps.size>0:
            if self.opt['nsub']>1: 
                # Gluing of properties from multiple sub-files
                apy.shell.exit('Property gluing is not implemented')
            else: 
                # Get property from a single file
                data = getProperty({
                    'sinkOpt':  self.opt['sinkOpt'],
                    'snapFile': self.sfileName[0],
                    'snapMode': self.opt['fmode'],
                    'comoving': self.opt['comoving'],
                    'chem':     self.optChem,
                },sProps,ids)
        else:
            data = {}
        
        # Load and insert complex properties
        for prop in aProps:
            if prop['key'] in data:
                aProps.setData(prop['key'], data[prop['key']])
            else:
                results = getattr(self, 'prop_'+prop['name'])(prop,ids)
                aProps.setData(prop['key'], results)

        # !! do not wrap np.array() around, because we want to return native array dtypes
        return aProps.getData(dictionary=dictionary)


# This function calculates (simple) properties
# It needs to be a global function if we want to use it on parallel cores
def getProperty(opt,properties,ids=None):

    # Construct a property class according to the chemistry type
    classes = (propSimple, propClass)
    if opt['chem']['type']=='sgchem1':
        classes = (propSgchem1,) + classes
    if opt['sinkOpt'] is not None:
        classes = (propSink,) + classes
    propList = type("propClass", classes, {})
        
    # Calculate properties and return values
    with propList(opt) as sp:
        return sp.getProperty(properties,ids,dictionary=True)
