import arepy as apy
import numpy as np
import inspect

def _foreach(fn,args,nproc,label,append,dataPrev=None):
    numDataAll = len(args)     # number of all data
    numDataOld = 0             # number of previous data
    if dataPrev:               # read new data only
        numDataOld = len(list(dataPrev.values())[0]) if isinstance(dataPrev,dict) else len(dataPrev)
        args = args[numDataOld:]
        if len(args)==0:       # return if there are no new items
            return dataPrev
    numDataNew = len(args)     # number of new data

    # use one or more cores to compute results of function 'fn'
    label = fn.__name__+' '+label if label else fn.__name__
    pb = apy.shell.pb(vmax=numDataNew,label=label) 
    if nproc>1:
        results = apy.util.parallelPool(fn,args,pbar=pb,nproc=nproc)
    else:
        results = []
        for arg in args: 
            results.append( fn(*arg) )
            pb.increase()
    pb.close()

    # rearrange data from all results
    adtypes = (str,apy.coord.regionBox,apy.coord.regionSphere,apy.coord.regionCone)
    dataNew = {}
    for index in range(numDataNew):
        result = results[index]
        keys   = list(result.keys())   if isinstance(result,dict) else ['nokey']
        values = list(result.values()) if isinstance(result,dict) else [result]
        numColumns = len(values)
        for c,key in enumerate(keys):
            if append or isinstance(values[c],adtypes):
                if index==0:
                    dataNew[key] = []
                dataNew[key].append(values[c])
            else:
                part = np.array(values[c])
                if index==0:
                    emptydata = np.zeros( (numDataNew,)+part.shape, dtype=part.dtype)
                    dataNew[key] = emptydata
                #if (data[key][index].shape!=part.shape):
                #    msg = "Length of partial '%s' data %d differs from collector array %d (foreach.py)"
                #    apy.shell.exit( msg%(key,len(part),len(data[key][index])) )
                dataNew[key][index] = part

    if dataPrev: # combine cached and new data
        keys   = list(dataPrev.keys())   if isinstance(dataPrev,dict) else ['nokey']
        values = list(dataPrev.values()) if isinstance(dataPrev,dict) else [dataPrev]
        numColumns = len(values)
        for c,key in enumerate(keys):
            if append or isinstance(values[c],str):
                dataNew[key] = dataPrev[key] + dataNew[key]
            else:
                dataNew[key] = np.concatenate((dataPrev[key],dataNew[key]),axis=0)

    # transform to an appropriate format
    if numDataAll==1: 
        dataNew = {key:value[0] for key,value in dataNew.items()}
    if numColumns==1:
        if 'nokey' in dataNew:
            dataNew = dataNew['nokey']
            
    # return data
    return dataNew

def foreach(fn,args,nproc=1,label='',append=False,dirCache=None,update=False):
    """For each argument from args perform a kernel function fn and return results

    :param function fn:  function that will be called
    :param list args:    list of arguments for the function
    :param int nproc:    number of processors
    :param str label:    label for cache and progress bar
    :param bool append:  force list appending instead of numpy preformated arrays
    :param str dirCache: if set, cache will be produced in this directory
    :param bool update:  update cached data if there are new arguments in args
    :return:             returns stacked data
    """

    # cache data if dirCache is set
    if dirCache:
        apy.shell.mkdir(dirCache,opt='u')
        nameCache = fn.__name__+'_'+label if label else fn.__name__
        return apy.data.cache( _foreach, nameCache, cacheDir=dirCache, args=[fn,args,nproc,label,append], update=update)
    else:
        data = _foreach(fn,args,nproc,label,append)
        return data
