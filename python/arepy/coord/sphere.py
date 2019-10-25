import arepy as apy
import numpy as np

class sphere:
    """Spherical region

    :param [float]*3 center: Center of a sphere
    :param float radius: Radius of a sphere
    :var [float]*3 center: Center of a sphere
    :var float radius: Radius of a sphere

    Example of use::
        
        >>> import arepy as apy
        >>> region = apy.coord.sphere([0.5,0.5,0.5],0.3)
        >>> region.show()
        
        Sphere class: center [0.5,0.5,0.5] radius 0.3
    """
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        True
    
    def __init__(self,*args):
        self.name = 'sphere'
        self.setRegion(center=args[0],radius=args[1])

    def getOuterBox(self,center=None,size=None):
        """Get outer box

        :param [float]*3 center: New box center
        :param float size: New box size
        :return: Region of the outer box
        :rtype: :class:`arepy.coord.box`
        """
        if center is None: center = self.center
        if size is None: size = self.radius*2
        return apy.coord.box(center,size)

    def getInnerBox(self,center=None,size=None):
        """Get inner box

        :param [float]*3 center: New box center
        :param float size: New box size
        :return: Region of the inner box
        :rtype: :class:`arepy.coord.box`
        """
        if center is None: center = self.center
        if size is None: size = self.radius*2/np.sqrt(3)
        return apy.coord.box(center,size)

    def show(self):
        """Print out region settings"""
        print("Sphere: center",self.center,"radius",self.radius)
        
    def getCopy(self):
        """Get copy of self"""
        return apy.coord.sphere(self.center,self.radius)        

    def setRegion(self,**args):
        """Set region settings"""
        if 'center' in args:
            self.center = np.array(args['center'][:],dtype=np.float32)
        if 'radius' in args:
            self.radius = args['radius']

    ##########################
    # Transformation routines
    ##########################

    # get sphere
    def getSphere(self):
        # do not ever return "self", because it is a pointer!!!
        return self.getCopy()

    def getBox(self):
        return self.getInnerBox()

    # select coordinates within the sphere
    def selectCoordinates(self,coord):
        x,y,z = (coord-self.center).T
        ids = (x*x + y*y + z*z) < self.radius**2
        if np.ndim(coord)>1:
            return ids, coord[ids]  # selector returns 2D array even though it was 1D before
        else:
            return ids, None if ids is False else coord


    # common transformations
    def setTranslation(self,origin):  # origin coordinates e.g: [0.5,0.5,0.5]
        self.setRegion(center=self.center-origin)
    def setFlip(self,flip):           # axes order e.g: [0,2,1]
        return
