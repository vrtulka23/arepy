import numpy as np
import arepy as apy
import h5py as hp

class snapSimple:

    # This function collects and reorders (simple) properties calculated on different cores
    def getPropertySimple(self,ptype,properties,ids=None):
        fmode = self.opt['fmode']
        nsub = self.opt['nsub']
        nproc = self.opt['nproc']
        comoving = self.opt['comoving']
        if nsub>1: # Get property from multiple files
            # Prepare arguments
            if ids is None: ids = [None for s in range(nsub)]
            arguments = []
            for s in range(nsub):
                arguments.append([s,self.sfileName[s],fmode,self.optChem,comoving,ptype,properties,ids[s]])
            # Use more cores for calculations if possible
            if nproc>1:
                allData = apy.util.parallelPool(getProperty,arguments,nproc=nproc)
            else:
                allData = [ getProperty(*arguments[s]) for s in range(nsub) ]
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
                name = prop['name']
                if name in getattr(apy.files,self.optChem['type']).const.dsets:
                    data[pid] = np.vstack(data[pid])
                elif name in apy.const.dsets:
                    data[pid] = np.vstack(data[pid])
                elif name in ['RadialRegion','BoxRegion']:
                    prop0 = [ s[0] for s in data[pid] ]
                    prop1 = [ s[1] for s in data[pid] ]
                    data[pid] = [ prop0, np.vstack(prop1) ] # we keep ids ordered by the file
                elif name in ['GridRegion']:
                    prop0 = [ s[0] for s in data[pid] ]
                    prop1 = [ s[1] for s in data[pid] ]
                    minids = np.argmin(prop1,axis=0) # find the results with the smallest distance
                    apy.shell.exit("TODO: 'GridRegion' for multiple snap files needs to be finished (snapSimple.py)")
                    data[pid] = [ prop0, prop1 ]
                    # TODO: select only particles with the lowest distance
                elif name in ['Histogram1D','Histogram2D']:
                    data[pid] = np.sum(data[pid],axis=0)
                elif name in ['Maximum','Minimum','Mean','MinPos','Sum']:
                    data[pid] = np.array(data[pid]).flatten()
                else:
                    data[pid] = np.hstack(data[pid])
        else: # Get property from a single file
            arguments = [ 0,self.sfileName[0],fmode,self.optChem,comoving,ptype,properties,ids ]
            data = getProperty(*arguments)
        for pid,prop in enumerate(properties):
            if data[pid] is None:
                apy.shell.exit("Property '%s' could not be calculated (snapSimple.py)"%prop['name'])
        return data

# This function calculates (simple) properties on every core separately
def getProperty(fnum,fileName,fmode,optChem,comoving,ptype,properties,ids=None):
    # Convert simple property names to dictionaries
    for pid in range(len(properties)):
        if isinstance(properties[pid],str):
            properties[pid] = {'name':properties[pid]}

    # Open the snapshot
    with hp.File(fileName,fmode) as sf:
        nPart = sf['Header'].attrs['NumPart_ThisFile'][ptype]
        # If there are no particles we return an empty array
        if nPart==0:
            return [[]]*len(properties)
        # If there are no selected particles we select all
        if ids is None:
            ids = slice(0,nPart)

    # Let's calculate all snapshot properties
    pt = 'PartType%d'%ptype
    nameStd=['ParticleIDs','Coordinates','Density',
             'InternalEnergy','ChemicalAbundances','PhotonRates','Coppied']
    nameCoord=['PosX','PosY','PosZ']
    nameStat=['Maximum','Minimum','Mean','MinPos','Sum']
    nameMath=['Plus','Minus','Multipy','Divide','Modulo']
    allData = []
    for prop in properties:
        name = prop['name']
        if name in nameStd:
            with hp.File(fileName,fmode) as sf:
                value = sf[pt][name][:]
            data = value[ids]

        elif name in nameCoord:                 # get a particular coordinate
            i = nameCoord.index(name)
            with hp.File(fileName,fmode) as sf:
                coord = sf[pt]['Coordinates'][:,i]
            data = coord[ids]

        elif name=='FileIndex':                 # index of the sub-snapshot file
            value = np.full(nPart,fnum)
            data = value[ids]

        elif name=='ParticleIndex':             # particle index within the file
            value = np.arange(nPart)
            data = value[ids]            

        elif name=='Radius':                    # in code [cm]
            with hp.File(fileName,fmode) as sf:
                coord = sf[pt]['Coordinates'][:]
            data = np.linalg.norm(coord[ids,:]-prop['center'],axis=1)

        elif name=='Radius2':                   # in code [cm^2]
            with hp.File(fileName,fmode) as sf:
                coord = sf[pt]['Coordinates'][:]
            coord = coord[ids,:] - prop['center']
            data = coord[:,0]**2 + coord[:,1]**2 + coord[:,2]**2

        elif name=='SelectIDs':
            with hp.File(fileName,fmode) as sf:
                pids = sf[pt]['ParticleIDs'][:]
            data = np.in1d(pids,prop['ids'])

        elif name=='RadialRegion':           # radius in code [cm^2]
            # Example: {'name':'RadialRegion','center':center,'radius':radius}
            with hp.File(fileName,fmode) as sf:
                coord = sf[pt]['Coordinates'][:]
            coord = coord[ids,:]-prop['center']
            r2 = coord[:,0]**2 + coord[:,1]**2 + coord[:,2]**2
            ids = r2 < prop['radius']**2
            data = [ ids, r2[ids] ]

        elif name=='BoxRegion':                 # coordinates in code [cm]
            # Example: {'name':'BoxRegion','box':box}
            with hp.File(fileName,fmode) as sf:
                coord = sf[pt]['Coordinates'][:]
            coord = np.array(coord[ids,:])
            box = np.array(prop['box'])
            ids = (box[0]<coord[:,0]) & (coord[:,0]<box[1]) & \
                (box[2]<coord[:,1]) & (coord[:,1]<box[3]) & \
                (box[4]<coord[:,2]) & (coord[:,2]<box[5])
            data = [ ids, coord[ids] ]

        elif name=='GridRegion':                # distances in code [cm]
            # Example: {'name':'GridRegion','grid':grid}
            with hp.File(fileName,fmode) as sf:
                coord = sf[pt]['Coordinates'][:]
            coord = coord[ids,:]     
            grid = prop['grid']
            from scipy.spatial import cKDTree
            kdt = cKDTree(coord)
            dist,ids = kdt.query(grid)
            data = [ ids, dist ]

        elif name=='Histogram1D':               # create histogram from a property
            # Example: bins=np.linspace(1,10,1)
            #          {'name':'Histogram1D','x':'PosX','bins':bins,'w':'Masses'}
            if 'weights' in prop:
                x, weights = getProperty(fnum,fileName,fmode,optChem,comoving,ptype,
                                    [prop['x'],prop['w']], ids=ids)
                hist,edges = np.histogram(x, bins=prop['bins'], 
                                          density=False, weights=weights)
            else:
                x = getProperty(fnum,fileName,fmode,optChem,comoving,ptype,
                                    [prop['x']], ids=ids)
                hist,edges = np.histogram(x, bins=prop['bins'], density=False)
            data = hist

        elif name=='Histogram2D':               # create a 2D histogram from a property
            # Example: bins=[np.linspace(1,10,1),np.linspace(2,12,2)]
            #          {'name':'Histogram2D','x':'PosX','y':'PosY','bins':bins,'w':'Masses'}
            if 'w' in prop:
                x, y, weights = getProperty(fnum,fileName,fmode,optChem,comoving,ptype,
                                    [prop['x'],prop['y'],prop['w']], ids=ids)
                hist,xedges,yedges = np.histogram2d(x, y, bins=prop['bins'], 
                                                    weights=weights) # density=False, 
            else:
                x, y = getProperty(fnum,fileName,fmode,optChem,comoving,ptype,
                                    [prop['x'],prop['y']], ids=ids)
                hist,xedges,yedges = np.histogram2d(x, y, bins=prop['bins']) #, density=False)
            data = hist

        elif name in nameStat:
            # Example: {'name':'Minimum','p':'PosX'}
            values = getProperty(fnum,fileName,fmode,optChem,comoving,ptype,[prop['p']],ids=ids)[0]
            if name=='Minimum': data = [np.min(values)]
            elif name=='MinPos': data = [np.min(values[values>0])] if np.any(values>0) else []
            elif name=='Maximum': data = [np.max(values)]
            elif name=='Mean': data = [np.mean(values)]
            elif name=='Sum': data = [np.sum(values)]

        elif name in nameMath:
            xval,yval = getProperty(fnum,fileName,fmode,optChem,comoving,ptype,[prop['x'],prop['y']],ids=ids)
            if name=='Plus': data = [xval+yval]
            elif name=='Minus': data = [xval-yval]
            elif name=='Multipy': data = [xval*yval]
            elif name=='Divide': data = [xval/yval]
            elif name=='Modulo': data = [xval%yval]

        else:
            # Setting functions according to the file type
            with hp.File(fileName,fmode) as sf:
                data = getattr(apy.files,optChem['type']).getProperty(sf,ptype,name,ids,comoving,optChem)
        
        # Append calculated data
        allData.append( data )
                        
    return allData
