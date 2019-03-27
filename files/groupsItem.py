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
        self.items = None

    # Set coordinate transformations
    def setTransf(self, **opt):
        self.transf = apy.coord.transf()   
        # pre-selection
        if 'box' in opt:
            center = (opt['box'][::2]+opt['box'][1::2])*0.5
            radius = np.linalg.norm(opt['box'][1::2]-opt['box'][::2])*0.5
            self.transf.addSelection('presphere', center, radius, opt['box'])
        elif 'center' in opt:
            if 'radius' in opt:
                self.transf.addSelection('preselect', opt['center'], opt['radius'])
            elif 'size' in opt:
                radius = opt['size']*np.sqrt(3)*0.5
                box = apy.coord.box(opt['size'],opt['center'])
                self.transf.addSelection('preselect', opt['center'], radius, box)
        # translation
        if 'origin' in opt:
            self.transf.addTranslation('translate', opt['origin'])
            if 'box' in opt:
                opt['box'] = self.transf.convert('translate',opt['box'],[0,0,1,1,2,2])
            if 'center' in opt:
                opt['center'] = self.transf.convert('translate',opt['center'],[0,1,2])
        # rotation
        if 'angles' in opt:
            self.transf.addRotation('rotate', opt['angles'])
        # post-select
        if 'box' in opt:
            self.transf.addSelection('postselect', opt['box'])
        elif 'center' in opt:
            if 'radius' in opt:
                self.transf.addSelection('postselect', opt['center'], opt['radius'])
            elif 'size' in opt:
                self.transf.addSelection('postselect', apy.coord.box(opt['size'],opt['center']))

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
