import multiprocessing as mpi

'''
Example:
def myFunction(q,i,args):
    ...producing results...
    q.put([i, results]) 

args = [['a',23],['b',22],['c',21],['d',343]]
print parallelize(myFunction,args)
'''
def parallelProcess(fn,tasks,pBar=False):
    nTasks = len(tasks)
    q = mpi.Queue(); g = []
    p = [ mpi.Process(target=fn, args=(q,i,tasks[i])) for i in range(nTasks) ]
    for i in range(nTasks): p[i].start()
    for i in range(nTasks):
        g.append( q.get() )
        if (pBar): pBar.increase()
    #    g = [ q.get(); pb for i in range(nTasks) ]
    for i in range(nTasks): p[i].join()
    data = [[]]*nTasks
    for i in range(nTasks):
        data[ g[i][0] ] = g[i][1]
    return data

'''
Example:
def myFunction(*args):
    ...producing results...
    return results
args = [['a',23],['b',22],['c',21],['d',343]]
print parallelPool(myFunction,args)
'''
def parallelPool(fn,args,pbar=False,nproc=16):
    nTasks = len(args)
    pool = mpi.Pool(processes=nproc)
    results = [pool.apply_async(_parallelPool, args=(i,fn,args[i])) for i in range(nTasks)]
    output = [[]]*nTasks
    for p in results:
        i,data = p.get()
        output[i]=data
        if (pbar): pbar.increase()
    pool.close()  # important to close and join, otherwise there will iddle 
    pool.join()   # threads hanging on the processor
    return output
def _parallelPool(i,fn,args):
    return [i, fn(*args)]
    
