import arepy as apy
import numpy as np

class cone:
    """Conical region

    :param [float]*3 center: Center of a cone
    :param float radius: Radius of a cone
    :param float theta: Openning angle of a cone (radians)
    :var [float]*3 center: Center of a cone
    :var float radius: Radius of a cone
    :var float theta: Openning angle of a cone (radians)

    Example of use::
        
        >>> import arepy as apy
        >>> import numpy as np
        >>> region = apy.coord.cone([0.5,0.5,0.5], 0.3, np.pi/4)
        >>> region.show()
        
        Cone class
        Center: [0.5,0.5,0.5]
        Radius: 0.3
        Theta: 0.785398
    """
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        True
    
    def __init__(self,*args):
        self.name = 'cone'
        self.setRegion(center=args[0],radius=args[1],theta=args[2])

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
        print("Cone class")
        print("Center:",self.center)
        print("Radius:",self.radius)
        print("Theta:", self.theta)
        
    ##########################
    # Transformation routines
    ##########################

    # get a sphere around the cone
    def getSphere(self):
        return apy.coord.sphere(self.center,self.radius)

    # select coordinates within the cone
    def selectCoordinates(self,coord):
        x,y,z = (coord-opt['center']).T
        theta = np.arccos( z / np.sqrt(x*x + y*y + z*z) )   # inclination 
        if (opt['theta']>0):  # around z-axis
            ids = (theta < opt['theta'])  | ( (np.pi-opt['theta']) < theta ) 
        else:                 # around x/y-plane
            ids = (-opt['theta'] < theta) | (theta < (opt['theta']+np.pi) )
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
        if 'theta' in args:
            self.theta = args['theta']

    # common transformations
    def setTranslation(self,origin):  # origin coordinates e.g: [0.5,0.5,0.5]
        self.setRegion(center=self.center-origin)
    def setFlip(self,flip):           # axes order e.g: [0,2,1]
        return
