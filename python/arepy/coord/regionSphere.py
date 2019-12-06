import arepy as apy
import numpy as np

class regionSphere:
    """Spherical region

    :param [float]*3 center: Center of a sphere
    :param float radius: Radius of a sphere
    :var [float]*3 center: Center of a sphere
    :var float radius: Radius of a sphere

    Example of use::
        
        >>> import arepy as apy
        >>> region = apy.coord.regionSphere([0.5,0.5,0.5],0.3)
        >>> region.show()
        
        Sphere class: center [0.5,0.5,0.5] radius 0.3
    """
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        True
    
    def __init__(self,*args,srad=None):
        self.name = 'sphere'
        self.setRegion(center=args[0],radius=args[1],srad=srad)

    def getOuterBox(self,center=None,size=None,srad=None):
        """Get outer box

        :param [float]*3 center: New box center
        :param float size: New box size
        :return: Region of the outer box
        :rtype: :class:`arepy.coord.regionBox`
        """
        if center is None: center = self.center
        if size is None: size = self.radius*2
        if srad is None: srad = self.srad
        return apy.coord.regionBox(center,size,srad=srad)

    def getInnerBox(self,center=None,size=None,srad=None):
        """Get inner box

        :param [float]*3 center: New box center
        :param float size: New box size
        :return: Region of the inner box
        :rtype: :class:`arepy.coord.regionBox`
        """
        if center is None: center = self.center
        if size is None: size = self.radius*2/np.sqrt(3)
        if srad is None: srad = self.srad
        return apy.coord.regionBox(center,size,srad=srad)

    def show(self):
        """Print out region settings"""
        print("Sphere: center",self.center,
              "radius",self.radius,
              "srad",self.srad)
        
    def setRegion(self,**args):
        """Set region settings"""
        if 'center' in args:
            self.center = np.array(args['center'][:],dtype=np.float32)
        if 'radius' in args:
            self.radius = args['radius']
        if 'srad' in args:
            self.srad = args['srad']

    ##########################
    # Transformation routines
    ##########################

    def getSelection(self):
        """Get a selection region"""
        radius = self.radius if self.srad is None else self.srad
        return apy.coord.regionSphere(self.center,radius)

    def getCopy(self):
        """Get copy of self"""
        return apy.coord.regionSphere(self.center,self.radius,srad=self.srad)        

    def selectCoordinates(self,coord):
        """Select coordinates within the region"""
        x,y,z = (coord-self.center).T
        ids = (x*x + y*y + z*z) < self.radius**2
        if np.ndim(coord)>1:
            return ids, coord[ids]  # selector returns 2D array even though it was 1D before
        else:
            return ids, None if ids is False else coord

    def setTranslation(self,origin): 
        """Apply translation on the region"""
        self.setRegion(center=self.center-origin)

    def setFlip(self,flip):
        """Flip the region"""
        self.setRegion(center=self.center[flip])
