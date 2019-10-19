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
        
        Sphere class
        Center: [0.5,0.5,0.5]
        Radius: 0.3
    """
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        True
    
    def __init__(self,*args):
        self.name = 'sphere'
        self.setRegion(center=args[0],radius=args[1])

    def getOuterBox(self):
        """Get outer box

        :return: Region of the outer box
        :rtype: :class:`arepy.coord.box`
        """
        return apy.coord.box(self.center,self.radius*2)

    def getInnerBox(self):
        """Get inner box

        :return: Region of the inner box
        :rtype: :class:`arepy.coord.box`
        """
        return apy.coord.box(self.center,self.radius*2/np.sqrt(3))

    def show(self):
        """Print out region settings"""
        print("Sphere class")
        print("Center:",self.center)
        print("Radius:",self.radius)    
        
    ##########################
    # Transformation routines
    ##########################

    # get sphere
    def getSphere(self):
        return apy.coord.sphere(self.center,self.radius)

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

    # update settings
    def setRegion(self,**args):
        if 'center' in args:
            self.center = np.array(args['center'],dtype=np.float32)
        if 'radius' in args:
            self.radius = args['radius']

    # common transformations
    def setTranslation(self,origin):  # origin coordinates e.g: [0.5,0.5,0.5]
        self.setRegion(center=self.center-origin)
    def setFlip(self,flip):           # axes order e.g: [0,2,1]
        return
