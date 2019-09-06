import numpy as np

# create field with box sizes (xmin, xmax, ymin, ymax, zmin, zmax)
def box(boxSize,boxCenter,show=False):
    rx,ry,rz = [boxSize*0.5]*3 if np.isscalar(boxSize) else np.array(boxSize)/2
    x,y,z = boxCenter
    dim = np.array([x-rx, x+rx, y-ry, y+ry, z-rz, z+rz])
    if show:
        print( dim[0], dim[1], dim[2], dim[3], dim[4], dim[5] )
    return dim 
