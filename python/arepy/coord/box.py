import arepy as apy
import numpy as np

class box:
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        True
    
    def __init__(self,*args):
        self.name = 'box'
        if len(args)==2:
            self.setRegion(center=args[0],size=args[1])
        else:
            self.setRegion(limits=args[0])

    # get a sphere around the box
    def getOuterSphere(self):
        radius = np.linalg.norm(self.size)*0.5
        return apy.coord.sphere(self.center,radius)

    # get a sphere inside the box
    def getInnerSphere(self):
        radius = np.min(self.size)*0.5
        return apy.coord.sphere(self.center,radius)

    # show box settings
    def show(self):
        print("Box class")
        print("Center:",self.center)
        print("Size:",self.size)
        print("Limits:",self.limits)


    ##########################
    # Transformation routines
    ##########################
    
    # return sphere around the box
    def getSphere(self):
        return self.getOuterSphere()

    # select coordinates inside of the box
    def selectInner(self,coord):
        x,y,z = coord.T
        ids =  (self.limits[0]<x) & (x<self.limits[1]) &\
               (self.limits[2]<y) & (y<self.limits[3]) &\
               (self.limits[4]<z) & (z<self.limits[5])
        return ids, coord[ids]

    # update settings
    def setRegion(self,**args):
        if 'limits' in args: # input parameter are box limits
            self.limits = np.array(args['limits'],dtype=np.float32)
            self.center = (self.limits[::2]+self.limits[1::2]) / 2
            self.size = (self.limits[1::2]-self.limits[::2])
        else:                # input parameter is box center and side sizes
            if 'center' in args:
                self.center = np.array(args['center'],dtype=np.float32)
            if 'size' in args:
                if np.isscalar(args['size']): 
                    self.size = np.full(3,args['size'],dtype=np.float32) 
                else:
                    self.size = np.array(args['size'],dtype=np.float32)
            self.limits = np.reshape([self.center-self.size/2,self.center+self.size/2],6,order='F')

    # common transformation
    def setTranslation(self,origin):  # origin coordinates e.g: [0.5,0.5,0.5]
        self.setRegion(limits=self.limits-origin[[0,0,1,1,2,2]])
    def setFlip(self,flip):           # axes order e.g: [0,2,1]
        limits = np.reshape(self.limits,(2,3),order='F')
        limits = limits.T[flip].T
        limits = np.reshape(limits,(6,),order='F')
        self.setRegion(limits=limits)
        
