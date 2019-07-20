import numpy as np
import arepy as apy
import h5py as hp
from arepy.files.snapPropertiesSimple import *

class snapSimple:
    # This function collects and reorders (simple) properties calculated on different cores
    def getPropertySimple(self,properties,ids=None):
        
        if self.opt['nsub']>1: # Get property from multiple files
            # Prepare arguments
            if ids is None: ids = [None for s in range(self.opt['nsub'])]
            arguments = []
            for s in range(self.opt['nsub']):
                arguments.append([s,self.sfileName[s],self.opt['fmode'],self.optChem,
                                  self.opt['comoving'],properties,ids[s]])
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

    sp = snapPropertiesSimple(fileName,fmode,fnum)

    # Read number of particles in each type
    with hp.File(fileName,fmode) as sf:
        nPart = sf['Header'].attrs['NumPart_ThisFile']

    # Let's calculate all snapshot properties
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

        if sp.hasProperty(prop):
            data = sp.getProperty(prop,ids)

        else:
            # If there are no selected particles we select all
            if ids is None:
                ids = slice(0,nPart[prop['ptype']])

            # Setting functions according to the file type
            with hp.File(fileName,fmode) as sf:
                data = getattr(apy.files,optChem['type']).getProperty(sf,prop['ptype'],prop['name'],ids,comoving,optChem)
        
        # Append calculated data
        allData.append( data )
                        
    return allData
