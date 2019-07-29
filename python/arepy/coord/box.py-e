import numpy as np

# create field with box sizes (xmin, xmax, ymin, ymax, zmin, zmax)
def box(boxSize,boxCenter,show=False):
    r = boxSize*0.5
    x,y,z = boxCenter
    dim = np.array([x-r, x+r, y-r, y+r, z-r, z+r])
    if show:
        print( dim[0], dim[1], dim[2], dim[3], dim[4], dim[5] )
    return dim 
