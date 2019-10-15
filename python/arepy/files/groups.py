import numpy as np
import arepy as apy
from arepy.files.groupsMethods import *

#############################
# Overload collection class #
#############################
class collection(apy.data.groups.collection):
    """Collection of groups
    
    :param list[str] names: List of group names
    :param list[dict] options: List of group settings
    """
    def __init__(self,names=None,options=None,**opt):
        super().__init__(names=names,options=options,**opt)

    def _addGroup(self):
        return group(**self.opt)
        
########################
# Overload group class #
########################
class group(apy.data.groups.group, groupsMethods):
    """Snapshot group

    :param int sim: Simulation ID
    :param list[int] snaps: Snapshot number or list of numbers
    """
    def __init__(self,sim=None,snaps=None,**opt):
        super().__init__(**opt)

        if sim is not None:
            self.addSnapshot(sim,snaps)

    def _addItem(self,opt,sim,snap):

        return item(self.size,self.name,opt,sim,snap)

    def addSnapshot(self,sim,snaps,opt=None):
        snaps = [int(snaps)] if np.isscalar(snaps) else [int(s) for s in snaps]
        if opt is None or isinstance(opt,dict):
            opt = [opt]*len(snaps) 
        for i,s in enumerate(snaps):
            self.addItem(opt[i],sim,int(s))

#######################
# Overload item class #
#######################
class item(apy.data.groups.item):
    """Snapshot item
    
    :var apy.files.simulation sim: Simulation
    :var apy.files.units units: Units 
    :var int snap: Default snapshot number
    :var apy.coord.transf transf: Transformations
    
    This class holds all information about a particular snapshot that should be analyzed
    """

    def __init__(self,index,groupName,opt,sim,snap):
        super().__init__(index,groupName,opt)
        self.sim = sim
        self.units = self.sim.units
        self.snap = snap
        self.transf = None

    # Set coordinate transformations
    def setTransf(self, **opt):
        """Set transformations"""
        self.transf = apy.coord.transf(**opt)   

    # snapshot file
    def getSnapshot(self,snap=None,**opt):
        """Get a snapshot object
        
        :param int snap: If not specified the default snapshot number of this item is used
        """
        if snap is None:
            snap = self.snap
        return self.sim.getSnapshot(snap,**opt)

    # sink file
    def getSink(self,snap=None,**opt):
        """Get a sink particle snapshot object

        :param int snap: If not specified the default snapshot number of this item is used
        """
        if snap is None:
            snap = self.snap
        return self.sim.getSink(snap,**opt)

    # image file
    def getImage(self,imProp,imType,snap=None,**opt):
        """Get an image object
        
        :param str imProp: Image property
        :param str imType: Image type (slice/proj)
        :param int snap: If not specified the default snapshot number of this item is used
        """
        if snap is None:
            snap = self.snap
        return self.sim.getImage(snap,imProp,imType,**opt)

    def getParameters(self):
        """Get a parameter file object of the simulation"""
        return self.sim.getParameters()
