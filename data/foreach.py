'''
def foreach(fn,data,keys,args=None):
    ndata = int(keys) if np.isscalar(keys) else len(keys)
    data = [data] if ndata==1 else data
    if np.isscalar(keys):
        results = [fn(data[i],*args) for i in range(ndata)]
    else:
        results = [keys[i]:fn(data[i],*args) for i in range(ndata)]
    return results[0] if ndata==1 else results
'''

def foreach(fn,values):
    if isinstance(values,(str,int,float)):
        return fn(values)
    else:
        return [ fn(value) for value in values ]
        
def forkeys(fn,keys):
    if isinstance(keys,str):
        return fn(value)
    else:
        return {key:fn(key) for key in keys}       
