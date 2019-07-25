import arepy as apy
import numpy as np

'''
input parameter 'data' is a set of data pairs: 
interp( x1,y1, x2,y2, x3,y3,... )
'''

def interp(*data):
    nData = len(data)/2
    xids = 2*np.arange(nData)
    # Find the x range
    xmin = np.max([ np.min(data[i]) for i in xids ])
    xmax = np.min([ np.max(data[i]) for i in xids ])
    if xmin>xmax:
        apy.shell.exit('Datasets do not intersect: xmin=%e > xmax=%e'%(xmin,xmax))
    # Find the coursness of the interpolation
    xnum = np.min([ np.sum((xmin<data[i])&(data[i]<xmax)) for i in xids ])
    if xnum<2:
        apy.shell.exit('Not enough points in the intersection: xnum=%d'%xnum)
    # Iterpolate data with the new base
    x = np.linspace(xmin,xmax,xnum)
    y = [ np.interp(x,data[i],data[i+1])  for i in xids ]
    return [x] + y
