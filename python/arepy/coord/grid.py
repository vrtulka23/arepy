import arepy as apy
import numpy as np

class grid:
    def __init__(self,bins=0,extent=None,points='centers',scatter=None,**opt):
        self.bins = [bins] if np.isscalar(bins) else bins
        self.nbins = [(b if np.isscalar(b) else len(b)) for b in self.bins]
        self.ndim = len(self.bins)
        self.scatter = scatter
        if extent is None:
            self.extent = np.array([[0,1],[0,1],[0,1]]) 
        else:
            self.extent = np.reshape(extent,(int(len(extent)/2),2),'C')
        if points=='centers':
            shift = [ (self.extent[b,1]-self.extent[b,0])*0.5/self.bins[b] for b in range(self.ndim) ]
            self.xi = [ np.linspace(self.extent[b,0],self.extent[b,1],self.bins[b],endpoint=False)+shift[b] for b in range(self.ndim) ]
        elif points=='edges':
            self.xi = [ np.linspace(self.extent[b,0],self.extent[b,1],self.bins[b]) for b in range(self.ndim) ] 
        coord,shape = self._setCoordinates(**opt)
        self.coords = coord
        self.shape = shape
        self.indexes = np.arange(len(coord)).reshape(tuple(shape))

    def _setScatter(self,coord):
        if self.scatter is not None:
            coord += (np.random.rand(len(coord),self.ndim)-0.5) * self.scatter
        return coord

    def __getitem__(self,index):
        if ~np.isscalar(index):
            index = self.indexes[index]
        return self.coords[index]

    # convert data to some standardized shape
    def reshapeData(self,data):
        return data

###########################
# Grid Volumes
###########################
class gridCube(grid):
    """Create a point grid with a shape of a cube

    .. image:: ../../../results/examples/grids/cube/debug/cube000.png

    Download the :download:`source code <../../../python/scripy/examples/plots/grids/cube.py>` of the plot.
    """
    def _setCoordinates(self):
        self.xxi = np.meshgrid(*self.xi)
        # ordered as: x*ny*nz + y*nz + z
        coord = np.vstack([ np.ravel(self.xxi[1]), np.ravel(self.xxi[0]), np.ravel(self.xxi[2]) ]).T 
        self._setScatter(coord)

        self.npix = len(coord)
        self.data = {}

        # flat list of coordinates
        return coord, self.nbins

    def getPixFromCoord(self,coord):
        pixSize = (self.extent[:,1]-self.extent[:,0]) / self.nbins     # calculate pixel direction in each dimension
        coord = coord-self.extent[:,0]                                 # shift coordinates to origin
        return np.floor( coord / pixSize ).astype(int)                  # calculate pixel indexes        

    def addAtCoord(self,prop,coord,value):
        pix = self.getPixFromCoord(coord)
        self.addAtPix(prop,pix,value)

    def addAtPix(self,prop,pix,value):
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
            

###########################
# Grid Surfaces
###########################
class gridSquareXY(grid):
    """Create a point grid in a form of a square on the X/Y plane

    .. image:: ../../../results/examples/grids/squarexy/debug/squarexy000.png

    Download the :download:`source code <../../../python/scripy/examples/plots/grids/squarexy.py>` of the plot.
    """
    def _setCoordinates(self,zfill=None):
        self.xxi = np.meshgrid(*self.xi)
        # ordered as: x*ny + y
        coord = np.vstack([ np.ravel(self.xxi[1]), np.ravel(self.xxi[0]) ]).T 

        # flat list of coordinates
        if zfill is not None:
            coord = [[x,y,zfill] for (x,y) in coord]
        return np.array(coord), self.nbins

    def reshapeData(self,data):
        return data.reshape(self.nbins)

class gridFieldXY(gridSquareXY):
    def reshapeData(self,data):
        return data

class gridHealpix(grid):
    """Create a point grid from a healpix sphere pixels

    .. image:: ../../../results/examples/grids/healpix/debug/healpix000.png

    Download the :download:`source code <../../../python/scripy/examples/plots/grids/healpix.py>` of the plot.
    """
    def _setCoordinates(self,nside=4,radius=1): 
        import healpy as hp
        npix = hp.nside2npix(nside)
        coord = np.zeros((npix,3))
        for i in range(npix):
            coord[i,:] = hp.pix2vec(nside,i)
        coord *= radius
        return coord, [npix]

    def reshapeData(self,data):
        import healpix as hp
        # we rotate the mollview by 90 degrees around z-axis to properly match the x and y axes
        data = hp.visufunc.mollview(data,return_projected_map=True) #,rot=(135,0,0))
        return np.where(data==-np.inf,np.nan,data)

class gridDisc(grid):
    """Create a disc grid with from concentric circles

    .. image:: ../../../results/examples/grids/disc/debug/disc000.png

    Download the :download:`source code <../../../python/scripy/examples/plots/grids/disc.py>` of the plot.
    """
    # Different parts of the disk can be located using offsets in 'self.parts'
    def __init__(self,bins,extent=None,points='edges',scatter=None,**opt):
        super().__init__(bins,extent,points,scatter,**opt)

    def _setCoordinates(self):
        coord = [[0,0,0]]
        self.parts = [1]
        for r,rb in enumerate(self.xi[0]):
            if r==0: continue
            lrbin = self.xi[0][r]-self.xi[0][r-1]  # radial bin length
            lcircle = 2 * np.pi * rb               # circumference length
            nabins = int(lcircle/lrbin)            # number of angular bins
            if nabins<2: continue
            self.parts.append( nabins )            # particle offests for different radii
            abins = np.linspace(0,2*np.pi,nabins,endpoint=False) # angular bins
            for a,ab in enumerate(abins):
                coord.append([rb*np.cos(ab),rb*np.sin(ab),0])
        self._setScatter(coord)
        self.split = np.cumsum(self.parts[:-1])    # particle split indexes
        return np.array(coord), [len(coord)]

    def reshapeData(self,data):
        return np.split(data, self.split)

###########################
# Grid Lines
###########################
class gridLine(grid):
    def _setCoordinates(self,yfill=None,zfill=None):
        coord = self.xi[0]
        self._setScatter(coord)
        self.parts = [len(coord)]
        # flat list of coordinates
        if zfill is not None and yfill is not None:
            coord = [[x,yfill,zfill] for x in coord]
        return coord, [len(coord)]

# carthesian line profiles X/Z
class gridLineXYZ(gridLine):
    def _setCoordinates(self,xfill=None,yfill=None,zfill=None):
        xcoord, shape = super()._setCoordinates(yfill=yfill,zfill=zfill)
        self.parts = self.parts+[len(self.xi[1]),len(self.xi[2])]  # update particle offset
        self.split = np.cumsum(self.parts[:-1])                    # update particle slit indexes
        ycoord = [[xfill,y,zfill] for y in self.xi[1]]        
        zcoord = [[xfill,yfill,z] for z in self.xi[2]]        
        return np.concatenate((xcoord,ycoord,zcoord),axis=0), [shape[0]+len(ycoord)+len(zcoord)]    

    def reshapeData(self,data):
        parts = np.split(data, self.split)
        return parts[0], parts[1], parts[2]

# polar line profiles R/Z
class gridLineRZ(gridDisc):
    def _setCoordinates(self,xfill=None,yfill=None):
        coord, shape = super()._setCoordinates()
        self.parts = self.parts+[len(self.xi[1])]  # update particle offset
        self.split = np.cumsum(self.parts[:-1])    # update particle split indexes
        zcoord = [[xfill,yfill,z] for z in self.xi[1]]        
        return np.concatenate((coord,zcoord),axis=0), [shape[0]+len(zcoord)]

    def reshapeData(self,data):
        parts = np.split(data, self.split)
        rline = np.array([np.mean(parts[i]) for i in range(0,len(parts)-1)])
        return rline, parts[-1]

# lines from a comon center using healpix
class gridRays(grid):
    """Create a grid of rays using healpix

    .. image:: ../../../results/examples/grids/rays/debug/rays000.png
    
    Download the :download:`source code <../../../python/scripy/examples/plots/grids/rays.py>` of the plot.
    """
    def _setCoordinates(self,nside=4):
        import healpy as hp
        self.npix = hp.nside2npix(nside)           # number of healpix pixels
        coord = np.zeros((self.npix,3))  
        for i in range(self.npix):
            coord[i,:] = hp.pix2vec(nside,i)
        nradii = len(self.xi[0])
        rays = np.zeros((nradii,self.npix,3))
        for b,radius in enumerate(self.xi[0]):
            rays[b] = coord*radius
        rays = np.vstack(rays)
        self.parts = [self.npix]*nradii            # updata particle offset
        self.split = np.cumsum(self.parts[:-1])    # update particle split indexes
        return rays, [len(rays)]

    def reshapeData(self,data):
        """Reshape data

        Reshapes data into the shape (npix,nbins)
        """
        return data.reshape((self.bins[0],self.npix)).T

# filled spherical grid using healpix
class gridSphere(grid):
    """Create a filled spherical grid using healpix

    .. image:: ../../../results/examples/grids/sphere/debug/sphere000.png
    
    Download the :download:`source code <../../../python/scripy/examples/plots/grids/sphere.py>` of the plot.
    """

    def _getHealpix(self,nside):
        import healpy as hp
        for i in range(10):
            print(i,hp.nside2npix(i))
        self.npix = hp.nside2npix(nside)           # number of healpix pixels
        coord = np.zeros((self.npix,3))  
        for i in range(self.npix):
            coord[i,:] = hp.pix2vec(nside,i)
        return coord
    
    def _setCoordinates(self,nside=4):
        vol = (4.*np.pi*self.xi[0]**3)/3. 

        coord = self._getHealpix(nside)
        nradii = len(self.xi[0])
        rays = np.zeros((nradii,self.npix,3))
        for b,radius in enumerate(self.xi[0]):
            rays[b] = coord*radius
        rays = np.vstack(rays)
        self.parts = [self.npix]*nradii            # updata particle offset
        self.split = np.cumsum(self.parts[:-1])    # update particle split indexes
        return rays, [len(rays)]

    def reshapeData(self,data):
        """Reshape data

        Reshapes data into the shape (npix,nbins)
        """
        return data.reshape((self.bins[0],self.npix)).T
