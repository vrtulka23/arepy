import arepy as apy
import numpy as np

class regionBox:
    """Box region

    :param [float]*3 center: Center of the box
    :param float size: Size or sizes of the box
    :type size: float or [float]*3
    :param [float]*6 limits: Box limits
    :var [float]*3 center: Center of a box
    :var float size: Size of a box
    :var [float]*6 limits: Box limits
    
    One can either set a center and size of the box, or only box limits.
    The other from the two settings will be automatically calculated::

        >>> import arepy as apy
        >>> region = apy.coord.regionBox([0.5,0.5,0.5], 0.3)
        >>> region.show()
        
        Box class
        Center: [0.5,0.5,0.5]
        Size: [0.3,0.3,0.3]
        Limits: [0.2,0.8,0.2,0.8,0.2,0.8]
        
        >>> region = apy.coord.regionBox([0.2,0.8,0.2,0.8,0.2,0.8])
        >>> region.show()

        Box class: center [0.5,0.5,0.5] size [0.3,0.3,0.3] limits [0.2,0.8,0.2,0.8,0.2,0.8] 
    """
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        True
    
    def __init__(self,*args,srad=None):
        self.name = 'box'
        if len(args)==2:
            self.setRegion(center=args[0],size=args[1],srad=srad)
        else:
            self.setRegion(limits=args[0],srad=srad)
    
    def getOuterSphere(self):
        """Get outer sphere

        :return: Region of the outer sphere
        :rtype: :class:`arepy.coord.regionSphere`
        """
        return apy.coord.regionSphere(self.center,self.radiusOuter,srad=self.srad)

    def getInnerSphere(self):
        """Get inner sphere

        :return: Region of the inner sphere
        :rtype: :class:`arepy.coord.regionSphere`
        """
        return apy.coord.regionSphere(self.center,self.radiusInner,srad=self.srad)

    def show(self):
        """Print out region settings"""
        print("Box: center",self.center,
              "size",self.size,
              "limits",self.limits,
              "srad",self.srad)

    def setRegion(self,**args):
        """Set region settings"""
        if 'limits' in args: # input parameter are box limits
            self.limits = np.array(args['limits'][:],dtype=np.float32)
            self.center = (self.limits[::2]+self.limits[1::2]) / 2
            self.size = (self.limits[1::2]-self.limits[::2])
        else:                # input parameter is box center and side sizes
            if 'center' in args:
                self.center = np.array(args['center'][:],dtype=np.float32)
            if 'size' in args:
                if np.isscalar(args['size']): 
                    self.size = np.full(3,args['size'],dtype=np.float32) 
                else:
                    self.size = np.array(args['size'][:],dtype=np.float32)
            self.limits = np.reshape([self.center-self.size/2,self.center+self.size/2],6,order='F')
        self.radiusOuter = np.linalg.norm(self.size)*0.5
        self.radiusInner = np.min(self.size)*0.5
        if 'srad' in args:
            self.srad = args['srad']

    ##########################
    # Transformation routines
    ##########################
    
    def getSelection(self):
        """Get a selection region"""
        radius = self.radiusOuter if self.srad is None else self.srad
        return apy.coord.regionSphere(self.center,radius)

    def getCopy(self):
        """Get copy of self"""
        return apy.coord.regionBox(self.limits,srad=self.srad)        

    def selectCoordinates(self,coord):
        """Select coordinates within the region"""
        x,y,z = coord.T
        ids =  (self.limits[0]<x) & (x<self.limits[1]) &\
               (self.limits[2]<y) & (y<self.limits[3]) &\
               (self.limits[4]<z) & (z<self.limits[5])
        return ids, coord[ids]

    def setTranslation(self,origin):
        """Applate translation on the region"""
        self.setRegion(limits=self.limits-np.array(origin)[[0,0,1,1,2,2]])
        
    def setFlip(self,flip):
        """Flip the region"""
        limits = np.reshape(self.limits,(2,3),order='F')
        limits = limits.T[flip].T
        limits = np.reshape(limits,(6,),order='F')
        self.setRegion(limits=limits)
        
