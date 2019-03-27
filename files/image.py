import numpy as np

# Read Arepo image files
def image( fileName, size=1, select=None ):
    with open(fileName, mode='rb') as f:
        npix_x = np.fromfile(f, np.uint32, 1)[0]
        npix_y = np.fromfile(f, np.uint32, 1)[0]            
        if size>1:
            images = np.fromfile(f, np.float32, npix_x*npix_y*size).reshape((npix_x, npix_y, size))
            image = images if select==None else images[:,:,select]
        else:
            image = np.fromfile(f, np.float32, npix_x*npix_y).reshape((npix_x, npix_y))
    return np.array(image), npix_x, npix_y
