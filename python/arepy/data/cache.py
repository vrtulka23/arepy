import arepy as apy
import numpy as np
import h5py as hp
import os

# Cache data into a numpy file or load from already existing numpy file
'''
Example:

def myFunct():
    ...some code that produces data...
    return data
data = cache(myFunct,'myCache',cacheDir='results')
...some code that uses the data...


DEBUG: if the following error occures, use simply a dictionary

In [31]: np.array([np.zeros((2, 2)), np.zeros((2,3))])
...
ValueError: could not broadcast input array from shape (2,2) into shape (2)
[ 0.,  0.]])], dtype=object)
'''

def _cacheLoad(cacheFile):
    data = np.load(cacheFile)
    return data.item() if data.size==1 else data
def cache( data, cacheName, cacheDir=None, reCache=False, args=[], update=False ):

    if cacheDir is None:
        cacheFile = '%s.npy'%(cacheName)
    else:
        cacheFile = '%s/%s.npy'%(cacheDir,cacheName)
    cacheFileShort = cacheFile #apy.util.shortPath(cacheFile)
    if not os.path.isfile(cacheFile) or reCache:
        if callable(data):
            data = data(*args,None) if update else data(*args)
        np.save(cacheFile,data)
        apy.shell.printc('Writing cache: "%s"'%cacheFileShort)
    else:
        if update: # update is only for incrementing
            oldData = _cacheLoad(cacheFile)
            data = data(*args,oldData) if callable(data) else data
            if oldData!=data:
                apy.shell.printc('Updating cache: "%s"'%cacheFileShort)
                np.save(cacheFile,data)
            else:
                apy.shell.printc('Reading cache: "%s"'%cacheFileShort)
        else:
            apy.shell.printc('Reading cache: "%s"'%cacheFileShort)

    return _cacheLoad(cacheFile)

class cacheH5:
    def __enter__(self):
        return self
    def __exit__(self, type, value, tb):
        return
    def __init__(self,name,verbose=False):
        self.f = hp.File(name,'a')
        self.verbose = verbose
        if self.verbose: apy.shell.printc('Caching file: '+name)

    def _checkGroups(self,dirname):
        # create path node list
        groups = []
        while dirname!="":
            path = dirname
            dirname,basename = os.path.split(dirname)
            groups.append( (path,dirname,basename) )
        groups.reverse()
        # create groups if not existing
        for path,dirname,basename in groups:
            if dirname=="" and basename not in self.f:   # check first node
                self.f.create_group(path)
            elif dirname!="" and basename not in self.f[dirname]:        # check other nodes
                self.f.create_group(path)

    def cache(self,path,data,args=[],update=False):
        dirname,basename = os.path.split(path)
        # check if all group exist
        self._checkGroups( dirname )
        # cache data if not existing
        if update and path in self.f:   
            if self.verbose: apy.shell.printc('Removing "%s"'%path)
            del self.f[path]
        if path not in self.f:
            if self.verbose: apy.shell.printc('Caching "%s"'%path)
            data = data(*args) if callable(data) else data
            self.f.create_dataset(path,data=data)
        else:
            if self.verbose: apy.shell.printc('Reading "%s"'%path)
        # return cached data
        return self.f[path][:]

    def read(self,path):
        if path not in self.f:
            apy.shell.exit("Path '%s' does not exists"%path)
        return self.f[path][:]

    def close(self):
        self.f.close()
