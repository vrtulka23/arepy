import arepy as apy
import numpy as np

class cone:
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        True
    
    def __init__(self,*args):
        self.name = 'cone'
        self.setRegion(center=args[0],radius=args[1],theta=args[2])

    # get a box around the original sphere
    def getOuterBox(self):
        return apy.coord.box(self.center,self.radius*2)

    # get a box inside the original sphere
    def getInnerBox(self):
        return apy.coord.box(self.center,self.radius*2/np.sqrt(3))

    # show cone settings
    def show(self):
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
