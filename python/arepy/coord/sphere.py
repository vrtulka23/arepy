import arepy as apy
import numpy as np

class sphere:
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        True
    
    def __init__(self,*args):
        self.name = 'sphere'
        self.setRegion(center=args[0],radius=args[1])

    # get a box around the sphere
    def getOuterBox(self):
        return apy.coord.box(self.center,self.radius*2)

    # get a box inside the sphere
    def getInnerBox(self):
        return apy.coord.box(self.center,self.radius*2/np.sqrt(3))

    # print sphere settings
    def show(self):
        print("Sphere class")
        print("Center:",self.center)
        print("Radius:",self.radius)    
        
    ##########################
    # Transformation routines
    ##########################

    # get sphere
    def getSphere(self):
        return self

    # select coordinates within the sphere
    def selectInner(self,coord):
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
