import numpy as np

# return statistics of the data
def stats(data,show=None):
    if show is None:
        show = ['min','median','mean','max','sum']
    stats = ""
    if 'min' in show:
        stats += " min=%.03e "%np.min(data)
    if 'median' in show:
        stats += " med=%.03e "%np.median(data)
    if 'mean' in show:
        stats += "mean=%.03e "%np.mean(data)
    if 'max' in show:
        stats += " max=%.03e "%np.max(data)
    if 'sum' in show:
        stats += " sum=%.03e "%np.sum(data)
    return stats
