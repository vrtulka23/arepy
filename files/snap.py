import numpy as np
import h5py as hp
import arepy as apy
import os
from arepy.files.snapComplex import *
from arepy.files.snapSimple import *

class snap(snapComplex,snapSimple):
    def __enter__(self):
        return self
    def __exit__(self, type, value, tb):
        return
    def __init__(self,fileName,**opt):
        self.initComplex()
        self.initSimple()

        default = apy.files.default['snap']
        self.fileName = fileName

        # set options
        self.opt = {
            'fmode':    'r',
            'nsub':     default['nsub'],
            'initChem': 'sgchem1',
            'comoving': False
            # other: nproc, nproc_ckdt
        }
        self.opt.update(opt)
        if 'nproc' not in self.opt:
            apy.shell.printc('Number of processors set to number of subfiles: %d'%self.opt['nsub'])
            self.opt['nproc'] = self.opt['nsub']
            
        # initialize chemistry
        self.initChem(self.opt['initChem'])

        # setup constants
        self.const = getattr(apy.files,self.optChem['type']).const
        
        # parse all file names
        if self.opt['nsub']>1:
            self.sfileName = [ self.fileName%f for f in range(self.opt['nsub']) ]
        else:
            self.sfileName = [ self.fileName ]

        for f in self.sfileName:
            if not os.path.isfile(f):
                apy.shell.prompt('File \"%s\"\ndoes not exits. Do you want to create new?'%f)
                hp.File(f,'w')

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
                return [data[name] for name in allNames]

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

    # This function switches between complex and simple properties
    # Example: sn.getProperty(['Masses',{'name':'Minimum','p':'PosX'}])
    def getProperty(self,props,ids=None):
        # Convert to array if needed
        aProps = [props] if isinstance(props,(str,dict)) else props
        nProps = len(aProps)

        sProps = []
        # Convert simple property names to dictionaries
        for pid in range(nProps):
            if isinstance(aProps[pid],str):
                aProps[pid] = {'name':aProps[pid]}
            if aProps[pid]['name'] not in self.cProps:
                sProps.append(aProps[pid])
        data = self.getPropertySimple(sProps, ids) if sProps else []
        for pid in range(nProps):
            if aProps[pid]['name'] in self.cProps:
                data.insert(pid, self.getPropertyComplex(aProps[pid],ids))

        # !! do not wrap np.array() around, because we want to return native array dtypes
        return data[0] if isinstance(props,(str,dict)) else data  
        '''
        if isinstance(props,(str,dict)):
            return data[0]
        else:
            return {aProps[p]['name']: data[p] for p in range(nProps)}
        '''
