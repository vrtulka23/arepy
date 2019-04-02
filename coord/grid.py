import numpy as np

'''
Example:

grid = apy.coord.grid([200,200],[0.4, 1.3, 4.3, 8.3])

'''

class grid:
    def __init__(self,bins,extent=None,points='centers',scatter=None,zfill=None):
        self.bins = [bins] if np.isscalar(bins) else bins
        self.nbins = [(b if np.isscalar(b) else len(b)) for b in self.bins]
        self.ndim = len(self.bins)
        if extent is None:
            self.extent = np.array([[0,1],[0,1],[0,1]]) 
        else:
            self.extent = np.reshape(extent,(int(len(extent)/2),2),'C')
        if points=='centers':
            shift = [ (self.extent[b,1]-self.extent[b,0])*0.5/self.bins[b] for b in range(self.ndim) ]
            self.xi = [ np.linspace(self.extent[b,0],self.extent[b,1],self.bins[b],endpoint=False)+shift[b] for b in range(self.ndim) ]
        elif points=='edges':
            self.xi = [ np.linspace(self.extent[b,0],self.extent[b,1],self.bins[b]) for b in range(self.ndim) ] 
        self.xxi = np.meshgrid(*self.xi)
        if self.ndim==3:   # ordered as: x*ny*nz + y*nz + z
            coord = np.vstack([ np.ravel(self.xxi[1]), np.ravel(self.xxi[0]), np.ravel(self.xxi[2]) ]).T 
        elif self.ndim==2: # ordered as: x*ny + y
            coord = np.vstack([ np.ravel(self.xxi[1]), np.ravel(self.xxi[0]) ]).T 
        else:              # ordered as: x
            coord = np.ravel(self.xxi[0])
        if scatter is not None:
            coord += (np.random.rand(len(coord),self.ndim)-0.5) * scatter

        # flat list of coordinates
        if self.ndim==2 and zfill is not None:
            coord3d = np.full((len(coord),3),zfill)
            coord3d[:,:2] = coord
            self.coords = coord3d
            self.grid = self.coords.reshape(tuple(self.nbins)+(3,))        
        else:
            self.coords = coord
            self.grid = self.coords.reshape(tuple(self.nbins)+(self.ndim,))        

        self.npix = len(self.coords)
        self.data = {}

    def getPixFromCoord(self,coord):
        pixSize = (self.extent[:,1]-self.extent[:,0]) / self.nbins  # calculate pixel direction in each dimension
        coord = coord-self.extent[:,0]                              # shift coordinates to origin
        pix = np.floor( coord / pixSize ).astype(int)               # calculate pixel indexes        
        return pix

    def addAtCoord(self,prop,coord,value):
        pix = self.getPixFromCoord(coord)
        self.addAtPix(prop,pix,value)

    def addAtPix(self,prop,pix,value):
        if self.ndim==3:
            if np.ndim(pix)>1:          # use only particles within the extent
                ids =  (0<=pix[:,0])&(pix[:,0]<self.nbins[0]) 
                ids &= (0<=pix[:,1])&(pix[:,1]<self.nbins[1])
                ids &= (0<=pix[:,2])&(pix[:,2]<self.nbins[2])
                pix,value = pix[ids],value if np.isscalar(value) else value[ids]
                npix = len(pix)
        if prop not in self.data:   # create a new data if it does not exists
            dshape = np.array(value).shape[1:]
            dtype = np.array(value).dtype
            self.data[prop] = np.zeros(tuple(self.nbins)+dshape,dtype=dtype)
        np.add.at( self.data[prop], tuple(pix.T), value )
            
    def __getitem__(self,index):
        if isinstance(index,tuple):
            if self.ndim==3:
                g = index[0]*self.nbins[1]*self.nbins[2] + index[1]*self.nbins[2] + index[2]
            elif self.ndim==2:
                g = index[0]*self.nbins[1] + index[1]
        else:
            g = index
        return self.coords[g]

