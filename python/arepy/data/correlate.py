import arepy as apy
import numpy as np

def correlate(xdata,ydata=None):
    if ydata is None:
        ydata = list(reversed(xdata))
    nx,ny = len(xdata), len(ydata)
    data = []
    for x in range(nx):
        for y in range(ny):
            if x<(nx-y-1):
                data.append((x,y,xdata[x],ydata[y]))
            else:
                continue
    return data
