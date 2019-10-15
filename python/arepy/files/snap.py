import numpy as np
import h5py as hp
import arepy as apy
import os

# Property list
from arepy.files.properties import *    # Property list class

# Property glues
from arepy.files.glueClass import *     # Parent class for property glues
from arepy.files.glueSimple import *    # Simple property glues

# Import property classes
import arepy.files.prop as pc

# Snapshot class
class snap(pc.complex,
           pc.complexRegion,
           pc.complexSlice,
           pc.complexProj):
    """Snapshot class

    :param str fileName: Path to the snapshot file
    :param dict initChem: Chemistry initialization settings
    :param dict sinkOpt: Sink particle file settings
    :return: Snapshot object

    Snapshot class is used to extract some data from the Arepo or sink snapshots and 
    it can be called within any Python script as follwos::

        >>> import arepy as apy
        >>> snap = apy.files.snap('./snap_001.hdf5')
    """

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
        """Set header values

        :param str name: Name of the header parameter
        :param value: Value of the header parameter
        :param int s: Index of a partial snapshot file. 
        """
        if isinstance(name,dict):
            for n,v in name.items():
                self._setHeader(n,v,s=s)
        else:
            self._setHeader(name,value,s=s)


    def getHeader(self,names=None,s=0):
        """Get header properties
        
        :param list[str] names: List of header properties.
        :param int s: Index of a partial snapshot file.
        :return: Property values
        """
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
        """Set a particle property

        :param int ptype: Particle type
        :param str name: Name of the parameter
        :param data: Dataset of the parameter
        :param list[bool] ids: Particle selector list
        :param int s: Index of a partial snapshot file.
        """
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
    def getProperty(self,props,ids=None,ptype=0,dictionary=False):
        """Get particle properties
        
        :param list(prop) props: Snapshot properties.
        :param list(bool) ids: Particle selector list.
        :param int ptype: Default particle type.
        :param bool dictionary: Return property values as dictionary only.
        :return: Property values

        Examples:
        
        1) Properties that do not need any additional settings can be called only using their name.
           Calling only a single property will return only values of the property::
        
            >>> snap.getProperty('Masses')
        
            [23.43, 34.23, 12.0, ...]
        
        2) Properties that need additional settings besides 'name', 'ptype' and 'ids' have to be called using a dictionary::
        
            >>> snap.getProperty({
            >>>     'name': 'SelectSphere',
            >>>     'center': [0.5,0.5,0.5],
            >>>     'radius': 0.2
            >>> })
        
            [True, False, False, ...]
        
        3) It is also possible to query for a list of properties.
           In this case the results will be given in a form of a dictionary like this::
        
            >>> snap.getProperty([
            >>>     'FormationOrder','Masses',
            >>>     {'name':'SelectFormationOrder','forder':[3,10,11]}
            >>> ])
        
            {'FormationOrder': [3, 23, 33, ...],
             'Masses':  [23.43, 34.23, 12.0, ...],
             'SelectFormationOrder': [True, False, False, ...]}
        
        4) It might be sometimes advantageous to return dictionaries also for single properties::
        
            >>> snap.getProperty('Masses', dictionary=True)
        
            {'Masses': [23.43, 34.23, 12.0, ...]}
        
        5) Property types can be set globally. The following example wil select masses and velocities of the sink particles only::
        
            >>> snap.getProperty([
            >>>     'Masses','ParticleIDs'
            >>> ], ptype=5)
        
            {'Masses': [23.43, 34.23, 12.0, ...],
             'ParticleIDs': [23, 233, 0, ...]}
        
        6) Property types can be also specified for each property individually.
           The following example will select masses of the gas particles, but velocities of the sink particles::
        
            >>> snap.getProperty([
            >>>     'Masses',
            >>>     {'name':'ParticleIDs', 'ptype':5}
            >>> ])
        
            {'Masses': [23.43, 34.23, 12.0, ...],
             'ParticleIDs': [13, 35, 22, ...]}
         
        7) If two properties in the list have a same name one has to be altered using a 'key' parameter::
        
            >>> snap.getProperty([
            >>>     'Masses',
            >>>     {'name':'Masses', 'ptype':5, 'key': 'SinkMasses'}
            >>> ])
        
            {'Masses': [23.43, 34.23, 12.0, ...],
             'SinkMasses': [13.23, 35.23, 22.0, ...]}
        
        8) It is also possible to directly input a property class::
            
            >>> properties = apy.files.properties(['Masses','Velocities'])
            >>> snap.getProperty(properties)
            
            {'Masses': [23.43, 34.23, 12.0, ...],
             'Velocities': [[23.34,26.6,834.3], [35.23, 22.0, 340,2], ...]}
        
        9) Note that some properties return subsets of values::

            >>> snap.getProperty({
            >>>     'name':'RegionSphere', 'center': [0.5]*3, 'radius': 0.5,
            >>>     'p': ['Masses','ParticleIDs']
            >>> })
                                                                                                                        
            {'Masses': [23.43, 34.23, 12.0, ...],                                                                                                           
             'ParticleIDs': [13, 35, 22, ...]}         
            
            >>> snap.getProperty([
            >>>     'Velocities',
            >>>     {'name':'RegionSphere', 'center': [0.5]*3, 'radius': 0.5, 
            >>>      'p': ['Masses','ParticleIDs']},
            >>> )
                                                                                                                        
            {'RegionSphere': {'Masses': [23.43, 34.23, 12.0, ...],
                              'ParticleIDs': [13, 35, 22, ...]},
             'Velocities': [[23.34,26.6,834.3], [35.23, 22.0, 340,2], ...]}   
        """
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
                },sProps,ids,ptype)
        else:
            data = {}
        
        # Load and insert complex properties
        for prop in aProps:
            if prop['key'] in data:
                aProps.setData(prop['key'], data[prop['key']])
            else:
                if 'ids' in prop:
                    print(prop)
                results = getattr(self, 'prop_'+prop['name'])(ids,**prop)
                aProps.setData(prop['key'], results)

        # !! do not wrap np.array() around, because we want to return native array dtypes
        return aProps.getData(dictionary=dictionary)

# This function calculates (simple) properties
# It needs to be a global function if we want to use it on parallel cores
def getProperty(opt,properties,ids=None,ptype=0):

    # Construct a property class according to the chemistry type
    classes = (
        pc.simple, 
        pc.simpleStat, 
        pc.simpleSelect, 
        pc.simpleMath, 
        pc.main
    )
    if opt['chem']['type']=='sgchem1':
        classes = (
            pc.sgchem1,
        ) + classes
    if opt['sinkOpt'] is not None:
        classes = (
            pc.sink,
            pc.sinkSelect
        ) + classes
    propList = type("main", classes, {})
        
    # Calculate properties and return values
    with propList(opt) as sp:
        return sp.getProperty(properties,ids,ptype=ptype,dictionary=True)
