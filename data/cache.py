import arepy as apy
import numpy as np
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


def cache( data, cacheName, cacheDir=None, reCache=False, args=None ):

    if cacheDir is None:
        cacheFile = 'cache_%s.npy'%(cacheName)
    else:
        cacheFile = '%s/cache_%s.npy'%(cacheDir,cacheName)
    if not os.path.isfile(cacheFile) or reCache:
        data = data(*args) if callable(data) else data
        np.save(cacheFile,data)
        print( apy.shell.textc('Caching data as "%s"'%cacheFile,'yellow') )
    else:
        print( apy.shell.textc('Reading cached data from "%s"'%cacheFile,'yellow') )

    data = np.load(cacheFile)
    return data.item() if data.size==1 else data
