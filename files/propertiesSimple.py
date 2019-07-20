import numpy as np
import arepy as apy
import h5py as hp

class propertiesSimple:
    def __init__(self,fileName,fmode,fnum,optChem,comoving):
        self.sf = hp.File(fileName,fmode)
        self.fileName = fileName
        self.fmode = fmode
        self.fnum = fnum

        self.comoving = comoving
        self.chem = optChem
        self.units = {
            'mass':    self.sf['Header'].attrs['UnitMass_in_g'],
            'length':  self.sf['Header'].attrs['UnitLength_in_cm'],
            'volume':  self.sf['Header'].attrs['UnitLength_in_cm']**3,
            'density': self.sf['Header'].attrs['UnitMass_in_g']/self.sf['Header'].attrs['UnitLength_in_cm']**3,
            'energy':  self.sf['Header'].attrs['UnitVelocity_in_cm_per_s']**2 * self.sf['Header'].attrs['UnitMass_in_g'],
        }
        if 'UnitPhotons_per_s' in self.sf['Parameters'].attrs:
            self.units['flux'] = self.sf['Parameters'].attrs['UnitPhotons_per_s']

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.sf.close()

    def hasProperty(self,prop):
        return hasattr(self,'property_'+prop['name'])

    def getProperty(self,prop,ids=None,dictionary=False):
        properties = apy.files.properties(prop)
        for pp in properties:
            if ids is None:
                npart = self.sf['Header'].attrs['NumPart_ThisFile'][pp['ptype']]
                indexes = slice(0,npart)
            else:
                indexes = ids
            properties.setData( pp['key'], getattr(self,'property_'+pp['name'])(pp,indexes) )
        return properties.getData(dictionary=dictionary)

    ########################
    # Direct properties
    ########################

    def _propDirect(self,prop,ids,name,select=None):
        dset = self.sf['PartType%d/%s'%(prop['ptype'],name)]
        data = dset[:,select] if select is not None else dset[:]
        return data[ids]

    def property_ParticleIDs(self,prop,ids):
        return self._propDirect(prop,ids,prop['name'])
    def property_Coordinates(self,prop,ids):
        return self._propDirect(prop,ids,prop['name'])
    def property_Masses(self,prop,ids):
        return self._propDirect(prop,ids,prop['name'])
    def property_Density(self,prop,ids):
        return self._propDirect(prop,ids,prop['name'])
    def property_Velocities(self,prop,ids):
        return self._propDirect(prop,ids,prop['name'])
    def property_InternalEnergy(self,prop,ids):
        return self._propDirect(prop,ids,prop['name'])
    def property_ChemicalAbundances(self,prop,ids):
        return self._propDirect(prop,ids,prop['name'])
    def property_PhotonRates(self,prop,ids):
        return self._propDirect(prop,ids,prop['name'])
    def property_Coppied(self,prop,ids):
        return self._propDirect(prop,ids,prop['name'])

    # position vector components
    def property_PosX(self,prop,ids):
        return self._propDirect(prop,ids,'Coordinates',0)
    def property_PosY(self,prop,ids):
        return self._propDirect(prop,ids,'Coordinates',1)
    def property_PosZ(self,prop,ids):
        return self._propDirect(prop,ids,'Coordinates',2)

    # velocity vector components
    def property_VelX(self,prop,ids):
        return self._propDirect(prop,ids,'Velocities',0)
    def property_VelY(self,prop,ids):
        return self._propDirect(prop,ids,'Velocities',1)
    def property_VelZ(self,prop,ids):
        return self._propDirect(prop,ids,'Velocities',2)

    ##########################
    # Indexes and counters
    ##########################

    # return selection indexes
    def property_Indexes(self,prop,ids):
        return ids

    # index of the sub-snapshot file
    def property_FileIndex(self,prop,ids):                 
        npart = self.sf['Header'].attrs['NumPart_ThisFile'][prop['ptype']]
        return np.full(npart,self.fnum)

    # particle index within the file
    def property_ParticleIndex(self,prop,ids):             
        data = np.arange(self.sf['Header'].attrs['NumPart_ThisFile'][prop['ptype']])
        return data[ids]            
    
    ##########################
    # Derived properties
    ##########################

    # radius from a given center
    def property_Radius(self,prop,ids):                    
        coord = self.sf['PartType%d/Coordinates'%prop['ptype']][:]
        coord = coord[ids,:] - prop['center']
        return np.linalg.norm(coord,axis=1)

    # quadrate of the radius from a given center
    def property_Radius2(self,prop,ids):                   
        coord = self.sf['PartType%d/Coordinates'%prop['ptype']][:]
        coord = coord[ids,:] - prop['center']
        return coord[:,0]**2 + coord[:,1]**2 + coord[:,2]**2
        
    # voronoi cell volume
    def property_CellVolume(self,prop,ids):                
        dens = self.sf['PartType%d/Density'%prop['ptype']][:]
        mass = self.sf['PartType%d/Masses'%prop['ptype']][:]
        return mass[ids]/dens[ids]
        
    # cell radius when assumed a spherical shape
    def property_CellRadius(self,prop,ids):                
        volume = self.property_CellVolume(prop,ids)
        return ((volume*3)/(4*np.pi))**(1./3.)

    # size of the velocity tangent component
    def property_VelocityRadial(self,prop,ids):            
        coord = self.sf['PartType%d/Coordinates'%prop['ptype']][:]
        vel = self.sf['PartType%d/Velocities'%prop['ptype']][:]
        rad = coord[ids,:]-prop['center']                   # translated origin
        norm = np.linalg.norm(rad,axis=1)[:,None]
        nhat = np.where(norm>0,rad/norm,np.zeros_like(rad)) # unit radial vector
        # taken from https://en.wikipedia.org/wiki/Tangential_and_normal_components
        return np.multiply(vel[ids,:],nhat).sum(1)       # element-wise dot product (v.n_hat)

    ##############################
    # ID selection regions
    ##############################

    # return indexes of particles with a specific ID
    def property_SelectIDs(self,prop,ids):
        pids = self.sf['PartType%d/ParticleIDs'%prop['ptype']][:]
        return np.in1d(pids,prop['ids'])

    def property_IDsRegion(self,prop,ids):
        pids = self.sf['PartType%d/ParticleIDs'%prop['ptype']][:]
        idsRegion = np.in1d(pids,prop['ids'])
        ids = np.where(ids, idsRegion, False)
        return self.getProperty(prop['p'],ids) if 'p' in prop else ids

    # radial region
    def property_RadialRegion(self,prop,ids): 
        # Example: {'name':'RadialRegion','center':center,'radius':radius,'p':'Mass'}
        coord = self.sf['PartType%d/Coordinates'%prop['ptype']][:]
        coord = coord[ids,:]-prop['center']
        r2 = coord[:,0]**2 + coord[:,1]**2 + coord[:,2]**2
        idsRegion = r2 < prop['radius']**2
        ids = np.where(ids, idsRegion, False)
        return self.getProperty(prop['p'],ids) if 'p' in prop else ids

    # box region
    def property_BoxRegion(self,prop,ids):    
        # Example: {'name':'BoxRegion','box':box,'p':'Mass'}
        coord = self.sf['PartType%d/Coordinates'%prop['ptype']][:]
        coord = np.array(coord[ids,:])
        box = np.array(prop['box'])
        idsRegion = (box[0]<coord[:,0]) & (coord[:,0]<box[1]) & \
                    (box[2]<coord[:,1]) & (coord[:,1]<box[3]) & \
                    (box[4]<coord[:,2]) & (coord[:,2]<box[5])
        ids = np.where(ids, idsRegion, False)
        return self.getProperty(prop['p'],ids) if 'p' in prop else ids

    # distances in code units
    def property_GridRegion(self,prop,ids):
        from scipy.spatial import cKDTree
        coord = sf['PartType%d/Coordinates'%prop['ptype']][:]
        coord = coord[ids,:]     
        grid = prop['grid']
        kdt = cKDTree(coord)
        dist,ids = kdt.query(grid)
        data = [ dist, ids ]
        #DEBUG: this must be still implemented for multiple snap files!!!!!
        return self.getProperty(prop['p'],ids) if 'p' in prop else ids

    ############################
    # Statistic functions
    ############################

    def property_StatMinimum(self,prop,ids):
        properties = apy.files.properties(prop['p'])
        data = self.getProperty(properties,ids,dictionary=True)
        for pp in properties:
            properties.setData( pp['key'], np.min(data[pp['key']]) )
        return properties.getData()

    def property_StatMinPos(self,prop,ids):
        properties = apy.files.properties(prop['p'])
        data = self.getProperty(properties,ids,dictionary=True)
        for pp in properties:
            ppdata = data[pp['key']]
            ppdata = [np.min(ppdata[ppdata>0])] if np.any(ppdata>0) else []
            properties.setData( pp['key'], np.min(values) )
        return properties.getData()

    def property_StatMaximum(self,prop,ids):
        properties = apy.files.properties(prop['p'])
        data = self.getProperty(properties,ids,dictionary=True)
        for pp in properties:
            properties.setData( pp['key'], np.max(data[pp['key']]) )
        return properties.getData()
        
    def property_StatMean(self,prop,ids):
        properties = apy.files.properties(prop['p'])
        data = self.getProperty(properties,ids,dictionary=True)
        for pp in properties:
            properties.setData( pp['key'], np.mean(data[pp['key']]) )
        return properties.getData()

    def property_StatSum(self,prop,ids):
        properties = apy.files.properties(prop['p'])
        data = self.getProperty(properties,ids,dictionary=True)
        for pp in properties:
            properties.setData( pp['key'], np.sum(data[pp['key']]) )
        return properties.getData()

    ############################
    # Mathematical functions
    ############################

    def property_MathPlus(self,prop,ids):
        properties = apy.files.properties([prop['x'],prop['y']])
        data = self.getProperty(properties,ids)
        return data[properties[0]['key']] + data[properties[1]['key']]        

    def property_MathMinus(self,prop,ids):
        properties = apy.files.properties([prop['x'],prop['y']])
        data = self.getProperty(properties,ids)
        return data[properties[0]['key']] - data[properties[1]['key']]        

    def property_MathMultiply(self,prop,ids):
        properties = apy.files.properties([prop['x'],prop['y']])
        data = self.getProperty(properties,ids)
        return data[properties[0]['key']] * data[properties[1]['key']]        

    def property_MathDivide(self,prop,ids):
        properties = apy.files.properties([prop['x'],prop['y']])
        data = self.getProperty(properties,ids)
        return data[properties[0]['key']] / data[properties[1]['key']]        

    def property_MathModulo(self,prop,ids):
        properties = apy.files.properties([prop['x'],prop['y']])
        data = self.getProperty(properties,ids)
        return data[properties[0]['key']] % data[properties[1]['key']]        

    ###########################
    # Histograms
    ###########################

    # create histogram from a property
    # Example: {'name':'Histogram1D','bins':np.linspace(1,10,1),'x':'PosX','w':'Masses'}
    def property_Histogram1D(self,prop,ids):
        properties = apy.files.properties(prop['x'])
        print('hello')
        if 'w' in prop:
            properties.add(prop['w'])
        data = self.getProperty(properties,ids,dictionary=True)
        weights = data[properties[1]['key']] if 'w' in prop else None
        hist,edges = np.histogram(data[properties[0]['key']], 
                                  bins=prop['bins'], density=False, weights=weights)
        return hist

    # create a 2D histogram from a property
    # Example: bins=[np.linspace(1,10,1),np.linspace(2,12,2)]
    #          {'name':'Histogram2D','x':'PosX','y':'PosY','bins':bins,'w':'Masses'}
    def property_Histogram2D(self,prop,ids):
        properties = apy.files.properties([prop['x'],prop['y']])
        if 'w' in prop:
            properties.add(prop['w'])
        data = self.getProperty(properties,ids,dictionary=True)
        weights = data[properties[2]['key']] if 'w' in prop else None
        hist,xedges,yedges = np.histogram2d(data[properties[0]['key']], data[properties[1]['key']], 
                                            bins=prop['bins'], weights=weights) #, density=False)
        return hist
            
