import numpy as np
import arepy as apy

#######################
# Snapshot item class #
#######################
class item:
    def __init__(self,index,sim,snap,groupName):
        self.index = index
        self.sim = sim
        self.snap = snap
        self.groupName = groupName

    # Set coordinate transformations
    def setTransf(self, **opt):
        self.transf = apy.coord.transf(**opt)   

    # snapshot file
    def getSnapshot(self,snap=None,**opt):
        if snap is None:
            snap = self.snap
        return self.sim.getSnapshot(snap,**opt)

    # sink file
    def getSink(self,snap=None,**opt):
        if snap is None:
            snap = self.snap
        return self.sim.getSink(snap,**opt)

    # image file
    def getImage(self,imProp,imType,snap=None,**opt):
        if snap is None:
            snap = self.snap
        return self.sim.getImage(snap,imProp,imType,**opt)
