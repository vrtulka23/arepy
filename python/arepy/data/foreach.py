import arepy as apy
import numpy as np
'''
Arguments:
fn       - function that will be called
args     - arguments for the function
nproc    - number of processors
label    - label for cache and progress bar
append   - force list appending instead of numpy preformated arrays
dirCache - if set, cache will be produced in this directory
'''

def _foreach(fn,args,nproc,label,append,udata=None):
    if udata: # read new data only
        nudata = len(list(udata.values())[0]) if isinstance(udata,dict) else len(udata)
        args = args[nudata:]
        if len(args)==0: # return if there are no new items
            return udata

    nargs = len(args)  # number of arguments
    append = append    # force to use appending into the list instead of formating numpy arrays

    # use one or more cores to compute results usin function 'fn'
    label = fn.__name__+' '+label if label else fn.__name__
    pb = apy.shell.pb(vmax=nargs,label=label) 
    if nproc>1:
        results = apy.util.parallelPool(fn,args,pbar=pb,nproc=nproc)
    else:
        results = []
        for arg in args: 
            results.append( fn(*arg) )
            pb.increase()
    pb.close()

    # rearrange data from the all results
    data = {}
    for index in range(nargs):
        result = results[index]
        keys   = list(result.keys())   if isinstance(result,dict) else ['data']
        values = list(result.values()) if isinstance(result,dict) else [result]
        ncols = len(values)
        for c,key in enumerate(keys):
            if append or isinstance(values[c],str):
                if index==0:
                    data[key] = []
                data[key].append(values[c])
            else:
                part = np.array(values[c])
                if index==0:
                    emptydata = np.zeros( (nargs,)+part.shape, dtype=part.dtype)
                    data[key] = emptydata
                #if (data[key][index].shape!=part.shape):
                #    msg = "Length of partial '%s' data %d differs from collector array %d (foreach.py)"
                #    apy.shell.exit( msg%(key,len(part),len(data[key][index])) )
                data[key][index] = part

    if udata: # combine cached and new data
        keys   = list(udata.keys())   if isinstance(udata,dict) else ['data']
        values = list(udata.values()) if isinstance(udata,dict) else [udata]
        ncols = len(values)
        for c,key in enumerate(keys):
            if append or isinstance(values[c],str):
                data[key] = udata[key] + data[key]
            else:
                print(key,udata[key].shape,data[key].shape)
                data[key] = np.concatenate((udata[key],data[key]),axis=0)

    # return appropriate format
    return data if ncols>1 else list(data.values())[0] 
def foreach(fn,args,nproc=1,label='',append=False,dirCache=None,update=False):
    # cache data if dirCache is set
    if dirCache:
        apy.shell.mkdir(dirCache,opt='u')
        nameCache = fn.__name__+'_'+label if label else fn.__name__
        return apy.data.cache( _foreach, nameCache, cacheDir=dirCache, args=[fn,args,nproc,label,append], update=update)
    else:
        return _foreach(fn,args,nproc,label,append)
