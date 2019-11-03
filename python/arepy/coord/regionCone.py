import arepy as apy
import numpy as np

class regionCone:
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
        >>> region = apy.coord.regionCone([0.5,0.5,0.5], 0.3, np.pi/4)
        >>> region.show()
        
        Cone: center [0.5,0.5,0.5] radius 0.3 theta 0.785398
    """
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        True
    
    def __init__(self,*args,srad=None):
        self.name = 'cone'
        self.setRegion(center=args[0],radius=args[1],theta=args[2],srad=srad)

    def show(self):
        """Print out region settings"""
        print("Cone: center",self.center,
              "radius",self.radius,
              "theta",self.theta,
              "srad",self.srad)

    def setRegion(self,**args):
        """Set region variables"""
        if 'center' in args:
            self.center = np.array(args['center'][:],dtype=np.float32)
        if 'radius' in args:
            self.radius = args['radius']
        if 'theta' in args:
            self.theta = args['theta']
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
        return apy.coord.regionCone(self.center,self.radius,self.theta,srad=self.srad)        

    def selectCoordinates(self,coord):
        """Select coordinates within the region"""
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

    def setTranslation(self,origin):
        """Apply translation on the region"""
        self.setRegion(center=self.center-origin)

    def setFlip(self,flip):
        """Flip the region"""
        self.setRegion(center=self.center[flip])

