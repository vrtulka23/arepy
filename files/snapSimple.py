import numpy as np
import arepy as apy
import h5py as hp

class snapSimple:
    # This function collects and reorders (simple) properties calculated on different cores
    def getPropertySimple(self,properties,ids=None):
        
        if self.opt['nsub']>1: # Get property from multiple files
            # Prepare arguments
            if ids is None: ids = [None for s in range(self.opt['nsub'])]
            arguments = []
            for s in range(self.opt['nsub']):
                arguments.append([s,self.sfileName[s],self.opt['fmode'],self.optChem,self.opt['comoving'],properties,ids[s]])
            # Use more cores for calculations if possible
            if self.opt['nproc']>1:
                allData = apy.util.parallelPool(getProperty,arguments,nproc=self.opt['nproc'])
            else:
                allData = [ getProperty(*arguments[s]) for s in range(self.opt['nsub']) ]
            # Combine data from all files
            data = []
            for pid,prop in enumerate(properties):
                subData = []
                for allDataSub in allData:
                    if allDataSub[pid] is None:
                        apy.shell.exit("Query of roperty '%s' returns 'None' value (snapSimple.py)"%prop['name'])
                    elif len(allDataSub[pid])>0:
                        subData.append( allDataSub[pid] )
                data.append( subData )
            # Arrange data to appropriate shapes
            for pid,prop in enumerate(properties):
                if prop['name'] in getattr(apy.files,self.optChem['type']).const.dsets:
                    data[pid] = np.vstack(data[pid])
                elif prop['name'] in apy.const.dsets:
                    data[pid] = np.vstack(data[pid])
                elif prop['name'] in ['GridRegion']:
                    prop0 = [ s[0] for s in data[pid] ]
                    prop1 = [ s[1] for s in data[pid] ]
                    minids = np.argmin(prop1,axis=0) # find the results with the smallest distance
                    apy.shell.exit("TODO: 'GridRegion' for multiple snap files needs to be finished (snapSimple.py)")
                    data[pid] = [ prop0, prop1 ]
                    # TODO: select only particles with the lowest distance
                elif not prop['complex']: # stack only for simple properties, return raw for complex properties
                    data[pid] = np.hstack(data[pid])
        else: # Get property from a single file
            arguments = [ 0,self.sfileName[0],self.opt['fmode'],self.optChem,self.opt['comoving'],properties,ids ]
            data = getProperty(*arguments)
        for pid,prop in enumerate(properties):
            if data[pid] is None:
                apy.shell.exit("Property '%s' could not be calculated (snapSimple.py)"%prop['name'])

        return data

# This function calculates (simple) properties on every core separately
def getProperty(fnum,fileName,fmode,optChem,comoving,properties,ids=None):
    # Make sure that the list of properties is properly initialized
    properties = apy.files.snapProperties(properties)

    # Read number of particles in each type
    with hp.File(fileName,fmode) as sf:
        nPart = sf['Header'].attrs['NumPart_ThisFile']

    # Let's calculate all snapshot properties
    nameStd=['ParticleIDs','Coordinates','Density',
             'InternalEnergy','ChemicalAbundances','PhotonRates','Coppied']
    nameCoord=['PosX','PosY','PosZ']
    nameStat=['Maximum','Minimum','Mean','MinPos','Sum']
    nameMath=['Plus','Minus','Multipy','Divide','Modulo']
    allData = []
    for prop in properties:
        # Set the particle type (default is gas)
        pt = 'PartType%d'%prop['ptype']

        # If there are no particles we return an empty array
        if nPart[prop['ptype']]==0:
            if prop['name'] in ['GridRegion','RadialRegion','BoxRegion']:
                if 'p' in prop:
                    if isinstance(prop['p'],(str,dict)):
                        allData.append( [[]]*(1+len(prop['p'])) )
                    else:
                        allData.append( [[],[]] )
                    continue
            allData.append( [] )
            continue

        # If there are no selected particles we select all
        if ids is None:
            ids = slice(0,nPart[prop['ptype']])

        if prop['name'] in nameStd:
            with hp.File(fileName,fmode) as sf:
                value = sf[pt][prop['name']][:]
            data = value[ids]

        elif prop['name'] in nameCoord:                 # get a particular coordinate
            i = nameCoord.index(prop['name'])
            with hp.File(fileName,fmode) as sf:
                coord = sf[pt]['Coordinates'][:,i]
            data = coord[ids]

        elif prop['name']=='FileIndex':                 # index of the sub-snapshot file
            value = np.full(nPart,fnum)
            data = value[ids]

        elif prop['name']=='ParticleIndex':             # particle index within the file
            value = np.arange(nPart)
            data = value[ids]            

        elif prop['name']=='Radius':                    # in code [cm]
            with hp.File(fileName,fmode) as sf:
                coord = sf[pt]['Coordinates'][:]
            data = np.linalg.norm(coord[ids,:]-prop['center'],axis=1)

        elif prop['name']=='Radius2':                   # in code [cm^2]
            with hp.File(fileName,fmode) as sf:
                coord = sf[pt]['Coordinates'][:]
            coord = coord[ids,:] - prop['center']
            data = coord[:,0]**2 + coord[:,1]**2 + coord[:,2]**2

        elif prop['name']=='CellVolume':
            with hp.File(fileName,fmode) as sf:
                dens = sf[pt]['Density'][:]
                mass = sf[pt]['Masses'][:]
            data = mass[ids]/dens[ids]

        elif prop['name']=='CellRadius':
            with hp.File(fileName,fmode) as sf:
                dens = sf[pt]['Density'][:]
                mass = sf[pt]['Masses'][:]
            data = ((mass[ids]*3)/(dens[ids]*4*np.pi))**(1./3.)

        elif prop['name']=='VelocityRadial':            # size of the velocity tangent component
            with hp.File(fileName,fmode) as sf:
                coord = sf[pt]['Coordinates'][:]
                vel = sf[pt]['Velocities'][:]
            rad = coord[ids,:]-prop['center']                   # translated origin
            norm = np.linalg.norm(rad,axis=1)[:,None]
            nhat = np.where(norm>0,rad/norm,np.zeros_like(rad)) # unit radial vector
            # taken from https://en.wikipedia.org/wiki/Tangential_and_normal_components
            tangent = np.multiply(vel[ids,:],nhat).sum(1)       # element-wise dot product (v.n_hat)
            data = tangent

        elif prop['name']=='SelectIDs':
            with hp.File(fileName,fmode) as sf:
                pids = sf[pt]['ParticleIDs'][:]
            data = np.in1d(pids,prop['ids'])

        elif prop['name']=='IDsRegion':
            with hp.File(fileName,fmode) as sf:
                pids = sf[pt]['ParticleIDs'][:]
            ids = np.in1d(pids[ids],prop['id']) # DEBUG: tends to be super slow for large arrays !!!
            if 'p' in prop: # return additional particle properties from the region
                retprop = [prop['p']] if isinstance(prop['p'],(str,dict)) else prop['p']
                retdata = getProperty(fnum,fileName,fmode,optChem,comoving,retprop,ids=ids)
                data = [ids] + retdata
            else:
                data = ids            

        elif prop['name']=='ConeRegion':
            data = None

        elif prop['name']=='RadialRegion': 
            # Example: {'name':'RadialRegion','center':center,'radius':radius,'p':'Mass'}
            with hp.File(fileName,fmode) as sf:
                coord = sf[pt]['Coordinates'][:]
            coord = coord[ids,:]-prop['center']
            r2 = coord[:,0]**2 + coord[:,1]**2 + coord[:,2]**2
            ids = r2 < prop['radius']**2
            if 'p' in prop: # return additional particle properties from the region
                retprop = [prop['p']] if isinstance(prop['p'],(str,dict)) else prop['p']
                retdata = getProperty(fnum,fileName,fmode,optChem,comoving,retprop,ids=ids)
                data = [ids] + retdata
            else:
                data = ids

        elif prop['name']=='BoxRegion':    
            # Example: {'name':'BoxRegion','box':box,'p':'Mass'}
            with hp.File(fileName,fmode) as sf:
                coord = sf[pt]['Coordinates'][:]
            coord = np.array(coord[ids,:])
            box = np.array(prop['box'])
            ids = (box[0]<coord[:,0]) & (coord[:,0]<box[1]) & \
                   (box[2]<coord[:,1]) & (coord[:,1]<box[3]) & \
                   (box[4]<coord[:,2]) & (coord[:,2]<box[5])
            if 'p' in prop: # return additional particle properties from the region
                retprop = [prop['p']] if isinstance(prop['p'],(str,dict)) else prop['p']
                retdata = getProperty(fnum,fileName,fmode,optChem,comoving,retprop,ids=ids)
                data = [ids] + retdata
            else:
                data = ids

        elif prop['name']=='GridRegion':                # distances in code [cm]
            # Example: {'name':'GridRegion','grid':grid}
            with hp.File(fileName,fmode) as sf:
                coord = sf[pt]['Coordinates'][:]
            coord = coord[ids,:]     
            grid = prop['grid']
            from scipy.spatial import cKDTree
            kdt = cKDTree(coord)
            dist,ids = kdt.query(grid)
            data = [ dist, ids ]
            if 'p' in prop: # return additional particle properties from the region
                retprop = [prop['p']] if isinstance(prop['p'],(str,dict)) else prop['p']
                retdata = getProperty(fnum,fileName,fmode,optChem,comoving,retprop,ids=ids)
                data = data + retdata

        elif prop['name']=='Histogram1D':               # create histogram from a property
            # Example: bins=np.linspace(1,10,1)
            #          {'name':'Histogram1D','x':'PosX','bins':bins,'w':'Masses'}
            if 'weights' in prop:
                x, weights = getProperty(fnum,fileName,fmode,optChem,comoving,
                                    [prop['x'],prop['w']], ids=ids)
                hist,edges = np.histogram(x, bins=prop['bins'], 
                                          density=False, weights=weights)
            else:
                x = getProperty(fnum,fileName,fmode,optChem,comoving,
                                    [prop['x']], ids=ids)
                hist,edges = np.histogram(x, bins=prop['bins'], density=False)
            data = hist

        elif prop['name']=='Histogram2D':               # create a 2D histogram from a property
            # Example: bins=[np.linspace(1,10,1),np.linspace(2,12,2)]
            #          {'name':'Histogram2D','x':'PosX','y':'PosY','bins':bins,'w':'Masses'}
            if 'w' in prop:
                x, y, weights = getProperty(fnum,fileName,fmode,optChem,comoving,
                                    [prop['x'],prop['y'],prop['w']], ids=ids)
                hist,xedges,yedges = np.histogram2d(x, y, bins=prop['bins'], 
                                                    weights=weights) # density=False, 
            else:
                x, y = getProperty(fnum,fileName,fmode,optChem,comoving,
                                    [prop['x'],prop['y']], ids=ids)
                hist,xedges,yedges = np.histogram2d(x, y, bins=prop['bins']) #, density=False)
            data = hist

        elif prop['name'] in nameStat:
            # Example: {'name':'Minimum','p':'PosX'}
            values = getProperty(fnum,fileName,fmode,optChem,comoving,[prop['p']],ids=ids)[0]
            if prop['name']=='Minimum': data = [np.min(values)]
            elif prop['name']=='MinPos': data = [np.min(values[values>0])] if np.any(values>0) else []
            elif prop['name']=='Maximum': data = [np.max(values)]
            elif prop['name']=='Mean': data = [np.mean(values)]
            elif prop['name']=='Sum': data = [np.sum(values)]

        elif prop['name'] in nameMath:
            xval,yval = getProperty(fnum,fileName,fmode,optChem,comoving,[prop['x'],prop['y']],ids=ids)
            if prop['name']=='Plus': data = [xval+yval]
            elif prop['name']=='Minus': data = [xval-yval]
            elif prop['name']=='Multipy': data = [xval*yval]
            elif prop['name']=='Divide': data = [xval/yval]
            elif prop['name']=='Modulo': data = [xval%yval]

        else:
            # Setting functions according to the file type
            with hp.File(fileName,fmode) as sf:
                data = getattr(apy.files,optChem['type']).getProperty(sf,prop['ptype'],prop['name'],ids,comoving,optChem)
        
        # Append calculated data
        allData.append( data )
                        
    return allData
