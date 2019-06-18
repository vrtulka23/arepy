import numpy as np
import arepy as apy

# return statistics of the data
def stats(name, data, show=None):
    if show is None:
        show = ['min','median','mean','max','sum']
    stats = "%-18s"%name
    for s in show:
        # statistical data
        stat = None
        if s=='min':
            stat = " min=%.03e "%np.min(data)
        elif s=='median':
            stat = " med=%.03e "%np.median(data)
        elif s=='mean':
            stat = "mean=%.03e "%np.mean(data)
        elif s=='max':
            stat = " max=%.03e "%np.max(data)
        elif s=='sum':
            stat = " sum=%.03e "%np.sum(data)
        elif s=='nanmin':
            stat = " nanmin=%.03e "%np.nanmin(data)
        elif s=='nanmax':
            stat = " nanmax=%.03e "%np.nanmax(data)
        elif s=='nansum':
            stat = " nansum=%.03e "%np.nansum(data)
        # health data
        elif s=='nan':  # not a number
            stat = " nan=%d "%np.isnan(data).sum()
        elif s=='isn':  # is number
            stat = " isn=%d "%np.sum(~np.isnan(data))
        elif s=='inf':
            stat = " inf=%d "%np.isinf(data).sum()
        elif s=='+inf':
            stat = " +inf=%d "%np.isposinf(data).sum()
        elif s=='-inf':
            stat = " -inf=%d "%np.isneginf(data).sum()
        elif s=='zero':
            stat = " zero=%d "%np.sum(data==0)
        elif s=='true':
            stat = " true=%d "%np.sum(data)
        elif s=='false':
            stat = " false=%d "%np.sum(~data)
        elif s=='len':
            stat = " len=%d "%len(data)
        elif s=='pos':
            stat = " pos=%d "%np.sum(data>0)
        elif s=='neg':
            stat = " neg=%d "%np.sum(data<0)
        if stat is None:
            apy.shell.exit('Invalid statistical opperation "%s" (stats.py)'%s)
        if s==show[-1]:
            stats += stat
        else:
            stats += "%-18s"%stat
    return stats
