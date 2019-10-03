import numpy as np
import arepy as apy
import h5py as hp

##################################
#
# A new property called NEW can be include simply by adding a new class method.
# For example:
#
# def prop_NEW(self,prop,ids):
#     return self.getSnapData('NEW',prop['ptype'],ids)
#
##################################

class propSimple:

    ########################
    # Direct properties
    ########################

    def prop_ParticleIDs(self,prop,ids):
        return self.getSnapData('ParticleIDs',prop['ptype'],ids)
    def prop_Masses(self,prop,ids):
        return self.getSnapData('Masses',prop['ptype'],ids)
    def prop_Density(self,prop,ids):
        return self.getSnapData('Density',prop['ptype'],ids)
    def prop_InternalEnergy(self,prop,ids):
        return self.getSnapData('InternalEnergy',prop['ptype'],ids)
    def prop_PhotonRates(self,prop,ids):
        return self.getSnapData('PhotonRates',prop['ptype'],ids)
    def prop_Coppied(self,prop,ids):
        return self.getSnapData('Coppied',prop['ptype'],ids)

    # position vector components
    def prop_Coordinates(self,prop,ids):
        return self.getSnapData('Coordinates',prop['ptype'],ids)
    def prop_PosX(self,prop,ids):
        return self.getSnapData('Coordinates',prop['ptype'],ids,0)
    def prop_PosY(self,prop,ids):
        return self.getSnapData('Coordinates',prop['ptype'],ids,1)
    def prop_PosZ(self,prop,ids):
        return self.getSnapData('Coordinates',prop['ptype'],ids,2)

    # velocity vector components
    def prop_Velocities(self,prop,ids):
        return self.getSnapData('Velocities',prop['ptype'],ids)
    def prop_VelX(self,prop,ids):
        return self.getSnapData('Velocities',prop['ptype'],ids,0)
    def prop_VelY(self,prop,ids):
        return self.getSnapData('Velocities',prop['ptype'],ids,1)
    def prop_VelZ(self,prop,ids):
        return self.getSnapData('Velocities',prop['ptype'],ids,2)

    ##########################
    # Indexes and counters
    ##########################

    # return selection indexes
    def prop_Indexes(self,prop,ids):
        return ids

    # index of the sub-snapshot file
    def prop_FileIndex(self,prop,ids):                 
        npart = self.sf['Header'].attrs['NumPart_ThisFile'][prop['ptype']]
        return np.full(npart,self.fnum)

    # particle index within the file
    def prop_ParticleIndex(self,prop,ids):             
        data = np.arange(self.sf['Header'].attrs['NumPart_ThisFile'][prop['ptype']])
        return data[ids]            
    
    ##########################
    # Derived properties
    ##########################

    # radius from a given center
    def prop_Radius(self,prop,ids):                    
        coord = self.prop_Coordinates(prop,ids) - prop['center']
        return np.linalg.norm(coord,axis=1)

    # quadrate of the radius from a given center
    def prop_Radius2(self,prop,ids):                   
        coord = self.prop_Coordinates(prop,ids) - prop['center']
        return coord[:,0]**2 + coord[:,1]**2 + coord[:,2]**2
        
    # size of the velocity tangent component
    def prop_VelocityRadial(self,prop,ids):            
        rad = self.prop_Coordinates(prop,ids) - prop['center']          # translated origin
        norm = np.linalg.norm(rad,axis=1)[:,None]
        nhat = np.where(norm>0,rad/norm,np.zeros_like(rad)) # unit radial vector
        # taken from https://en.wikipedia.org/wiki/Tangential_and_normal_components
        return np.multiply(self.prop_Velocities(prop,ids),nhat).sum(1)  # element-wise dot product (v.n_hat)

    # voronoi cell volume
    def prop_CellVolume(self,prop,ids):                
        return self.prop_Masses(prop,ids) / self.prop_Density(prop,ids)
        
    # cell radius when assumed a spherical shape
    def prop_CellRadius(self,prop,ids):                
        volume = self.prop_CellVolume(prop,ids)
        return ((volume*3)/(4*np.pi))**(1./3.)

    ##############################
    # Particle selections
    ##############################

    def prop_SelectIds(self,prop,ids):
        idsSelect = np.in1d(self.prop_ParticleIDs(prop,ids),prop['ids'])
        ids = np.where(ids, idsSelect, False)
        return self.getProperty(prop['p'],ids=ids,ptype=prop['ptype']) if 'p' in prop else ids

    # radial region
    def prop_SelectSphere(self,prop,ids): 
        # Example: {'name':'SelectSphere','center':center,'radius':radius,'p':'Mass'}
        coord = self.prop_Coordinates(prop,ids)-prop['center']
        r2 = coord[:,0]**2 + coord[:,1]**2 + coord[:,2]**2
        idsSelect = r2 < prop['radius']**2
        ids = np.where(ids, idsSelect, False)
        return self.getProperty(prop['p'],ids=ids,ptype=prop['ptype']) if 'p' in prop else ids

    # box region
    def prop_SelectBox(self,prop,ids):    
        # Example: {'name':'SelectBox','box':box,'p':'Mass'}
        coord = np.array(self.prop_Coordinates(prop,ids))
        box = np.array(prop['box'])
        idsSelect = (box[0]<coord[:,0]) & (coord[:,0]<box[1]) & \
                    (box[2]<coord[:,1]) & (coord[:,1]<box[3]) & \
                    (box[4]<coord[:,2]) & (coord[:,2]<box[5])
        ids = np.where(ids, idsSelect, False)
        return self.getProperty(prop['p'],ids=ids,ptype=prop['ptype']) if 'p' in prop else ids

    # distances in code units
    def prop_SelectPoints(self,prop,ids):
        from scipy.spatial import cKDTree
        coord = self.prop_Coordinates(prop,ids)
        grid = prop['grid']
        kdt = cKDTree(coord)
        dist,ids = kdt.query(grid)
        data = [ dist, ids ]
        #DEBUG: this must be still implemented for multiple snap files!!!!!
        return self.getProperty(prop['p'],ids=ids,ptype=prop['ptype']) if 'p' in prop else ids

    ############################
    # Statistic functions
    ############################

    def prop_StatMinimum(self,prop,ids):
        properties = apy.files.properties(prop['p'],ptype=prop['ptype'])
        data = self.getProperty(properties,ids,dictionary=True)
        for pp in properties:
            properties.setData( pp['key'], np.min(data[pp['key']]) )
        return properties.getData()

    def prop_StatMinPos(self,prop,ids):
        properties = apy.files.properties(prop['p'],ptype=prop['ptype'])
        data = self.getProperty(properties,ids,dictionary=True)
        for pp in properties:
            ppdata = data[pp['key']]
            ppdata = [np.min(ppdata[ppdata>0])] if np.any(ppdata>0) else []
            properties.setData( pp['key'], np.min(values) )
        return properties.getData()

    def prop_StatMaximum(self,prop,ids):
        properties = apy.files.properties(prop['p'],ptype=prop['ptype'])
        data = self.getProperty(properties,ids,dictionary=True)
        for pp in properties:
            properties.setData( pp['key'], np.max(data[pp['key']]) )
        return properties.getData()
        
    def prop_StatMean(self,prop,ids):
        properties = apy.files.properties(prop['p'],ptype=prop['ptype'])
        data = self.getProperty(properties,ids,dictionary=True)
        for pp in properties:
            properties.setData( pp['key'], np.mean(data[pp['key']]) )
        return properties.getData()

    def prop_StatSum(self,prop,ids):
        properties = apy.files.properties(prop['p'],ptype=prop['ptype'])
        data = self.getProperty(properties,ids,dictionary=True)
        for pp in properties:
            properties.setData( pp['key'], np.sum(data[pp['key']]) )
        return properties.getData()

    ############################
    # Mathematical functions
    ############################

    def prop_MathPlus(self,prop,ids):
        properties = apy.files.properties([prop['x'],prop['y']],ptype=prop['ptype'])
        data = self.getProperty(properties,ids)
        return data[properties[0]['key']] + data[properties[1]['key']]        

    def prop_MathMinus(self,prop,ids):
        properties = apy.files.properties([prop['x'],prop['y']],ptype=prop['ptype'])
        data = self.getProperty(properties,ids)
        return data[properties[0]['key']] - data[properties[1]['key']]        

    def prop_MathMultiply(self,prop,ids):
        properties = apy.files.properties([prop['x'],prop['y']],ptype=prop['ptype'])
        data = self.getProperty(properties,ids)
        return data[properties[0]['key']] * data[properties[1]['key']]        

    def prop_MathDivide(self,prop,ids):
        properties = apy.files.properties([prop['x'],prop['y']],ptype=prop['ptype'])
        data = self.getProperty(properties,ids)
        return data[properties[0]['key']] / data[properties[1]['key']]        

    def prop_MathModulo(self,prop,ids):
        properties = apy.files.properties([prop['x'],prop['y']],ptype=prop['ptype'])
        data = self.getProperty(properties,ids)
        return data[properties[0]['key']] % data[properties[1]['key']]        

    ###########################
    # Histograms
    ###########################

    # create histogram from a property in this sub-file
    # Example: {'name':'Hist1D','bins':np.linspace(1,10,1),'x':'PosX','w':'Masses'}
    def prop_Hist1D(self,prop,ids):
        properties = apy.files.properties(prop['x'],ptype=prop['ptype'])
        if 'w' in prop:
            properties.add(prop['w'])
        data = self.getProperty(properties,ids,dictionary=True)
        weights = data[properties[1]['key']] if 'w' in prop else None
        hist,edges = np.histogram(data[properties[0]['key']], 
                                  bins=prop['bins'], density=False, weights=weights)
        return hist

    # create a 2D histogram from a property in this sub-file
    # Example: bins=[np.linspace(1,10,1),np.linspace(2,12,2)]
    #          {'name':'Hist2D','x':'PosX','y':'PosY','bins':bins,'w':'Masses'}
    def prop_Hist2D(self,prop,ids):
        properties = apy.files.properties([prop['x'],prop['y']],ptype=prop['ptype'])
        if 'w' in prop:
            properties.add(prop['w'])
        data = self.getProperty(properties,ids,dictionary=True)
        weights = data[properties[2]['key']] if 'w' in prop else None
        hist,xedges,yedges = np.histogram2d(data[properties[0]['key']], data[properties[1]['key']], 
                                            bins=prop['bins'], weights=weights) #, density=False)
        return hist
