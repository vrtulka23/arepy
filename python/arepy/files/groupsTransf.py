import numpy as np
import arepy as apy

##########################################################
# This class prepares different standard transformations #
##########################################################

class groupsTransf:

    def __init__(self,item):
        self.item = item

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        return

    def getTransf(self,name,args):
        return getattr(self,'transf_'+name)(**args)

    # Get trasformation from a sink particle ID
    def transf_SinkID(self,lrad,ids,size=None):
        snap = self.item.getSnapshot()
        sid = self.item.opt[ids] if isinstance(ids,str) else ids[self.item.index]
        data = snap.getProperty({'name':'RegionIds','ptype':5,'pids':sid,'p':[
            {'name':'Coordinates','ptype':5},
            {'name':'Masses','ptype':5}
        ]})    
        if len(data['Masses'])>0:
            center = data['Coordinates'][0]         # select the most massive sink
            L = snap.getProperty({'name':'AngularMomentum','center':center,'radius':lrad})
            transf = {
                'origin':center,
                'align':L,
            }
            if size is not None:
                transf['region'] = apy.coord.box(center,size)
            else:
                transf['region'] = apy.coord.sphere(center,lrad)
            return transf
        else:
            return {
                'region': apy.coord.sphere([np.nan]*3,lrad),
                'origin': [np.nan]*3,
                'align':  [np.nan]*3,
            }

    # Get transformation from the position of the main sink particle
    def transf_MainSink(self,lrad,size=None):
        snap = self.item.getSnapshot()
        data = snap.getProperty([
            {'name':'Coordinates','ptype':5},
            {'name':'Masses','ptype':5}
        ])
        if len(data['Masses'])>0:
            ids = np.argmax(data['Masses'])
            center = data['Coordinates'][ids]         # select the most massive sink
            L = snap.getProperty({'name':'AngularMomentum','center':center,'radius':lrad})
            transf = {
                'origin':center,
                'align':L,
            }
            if size is not None:
                transf['region'] = apy.coord.box(center,size)
            else:
                transf['region'] = apy.coord.sphere(center,lrad)            
            return transf
        else:
            return {
                'region': apy.coord.sphere([np.nan]*3,lrad),
                'origin': [np.nan]*3,
                'align':  [np.nan]*3,
            }

    # Get transformation from the BoxSize value
    def transf_BoxSize(self):
        snap = self.item.getSnapshot()
        size = snap.getHeader('BoxSize')
        return {
            'center': [size/2]*3,
            'size':   size,
            'box':    [0,BoxSize,0,BoxSize,0,BoxSize],
        }

    # Get transformation from the Arepo image settings in parameter file
    def transf_ArepoImage(self):
        param = self.item.getParam()
        return {
            'box': param.getProperty(['PicXmin','PicXmax','PicYmin','PicYmax','PicZmin','PicZmax'])
        }
