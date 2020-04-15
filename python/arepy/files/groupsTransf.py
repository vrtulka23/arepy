import numpy as np
import arepy as apy

##########################################################
# This class prepares different standard transformations #
##########################################################

class groupsTransf:
    """Group transformation class
    """

    def __init__(self,item):
        self.item = item
        
        self.empty1 = {
            'region': apy.coord.regionSphere([np.nan]*3,np.nan),
            'origin': [np.nan]*3,
            'align':  [np.nan]*3,
        }

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        return

    def getTransf(self,args):
        if isinstance(args,str):
            name = args
            args = {}
        else:
            name = args.pop('name')
        return getattr(self,'transf_'+name)(**args)

    def _diskTransf(self,center,lrad,size=None,radius=None):
        snap = self.item.getSnapshot()

        # Set origin and region
        transf = {'origin':center}
        if size is not None:
            transf['region'] = apy.coord.regionBox(center,size)
        elif radius is not None:
            transf['region'] = apy.coord.regionSphere(center,radius)
        else:
            transf['region'] = apy.coord.regionSphere(center,lrad)

        # Get orientation of the angular momentum
        transf['align'] = snap.getProperty({'name':'AngularMomentum','center':center,'radius':lrad})

        # Adjust selection radius
        srad = snap.getProperty({
            'name':'SelectionRadius', 'center':center,
            'radius':transf['region'].getSelection().radius,
        })
        transf['region'].setRegion(srad=srad)        

        return transf

    ###################
    # Transformations #
    ###################

    def transf_SinkFormationOrder(self,lrad,forder,size=None,radius=None):
        """Get trasformation from a sink particle ID
        
        :param forder: string = item option key, int = formation order, list[int] = formation orders for each item
        """
        snap = self.item.getSnapshot()
        if isinstance(forder,str):  # forder is an item option key
            forder = self.item.opt[forder] 
        elif np.isscalar(forder):   # forder is a single formation order
            forder = forder
        else:
            forder[self.item.index] # forder is a list of formation order 
        data = snap.getProperty({'name':'RegionFormationOrder','forder':forder,'p':[
            'Coordinates','Masses'
        ]}, ptype=5)
        if len(data['Masses'])>0:
            return self._diskTransf(data['Coordinates'][0],lrad,size,radius)
        else:
            return self.empty1

    def transf_SinkID(self,lrad,ids,size=None,radius=None):
        """Get trasformation from a sink particle ID
        """
        snap = self.item.getSnapshot()
        sid = self.item.opt[ids] if isinstance(ids,str) else ids[self.item.index]
        data = snap.getProperty({'name':'RegionIDs','pids':sid,'p':[
            'Coordinates','Masses'
        ]}, ptype=5)    
        if len(data['Masses'])>0:
            return self._diskTransf(data['Coordinates'][0],lrad,size,radius)
        else:
            return self.empty1

    def transf_ParticleID(self,lrad,ids,size=None,radius=None,ptype=0):
        """Get trasformation from a particle ID
        """
        snap = self.item.getSnapshot()
        if isinstance(ids,str):
            pid = self.item.opt[ids] 
        elif np.isscalar(ids):
            pid = ids
        else:
            pid = ids[self.item.index]
        data = snap.getProperty({'name':'RegionIDs','pids':pid,'p':[
            'Coordinates','Masses'
        ]}, ptype=ptype)
        if len(data['Masses'])>0:
            return self._diskTransf(data['Coordinates'][0],lrad,size,radius)
        else:
            return self.empty1

    def transf_MainSink(self,lrad,size=None,radius=None):
        """Get transformation from the position of the main sink particle
        """
        snap = self.item.getSnapshot()
        data = snap.getProperty(['Coordinates','Masses'], ptype=5)
        if len(data['Masses'])>0:
            ids = np.argmax(data['Masses']) # select the most massive sink
            return self._diskTransf(data['Coordinates'][ids],lrad,size,radius)
        else:
            return self.empty1

    def transf_BoxSize(self):
        """Get transformation from the BoxSize value
        """
        snap = self.item.getSnapshot()
        BoxSize = snap.getHeader('BoxSize')
        limits = np.array([0,BoxSize,0,BoxSize,0,BoxSize])
        return {
            'center': limits[1::2]-limits[0::2],
            'region': apy.coord.regionBox(limits)
        }

    def transf_ArepoImage(self,zlim=None):
        """Get transformation from the Arepo image settings in parameter file
        """
        param = self.item.getParameters()
        limits = param.getValue(['PicXmin','PicXmax','PicYmin','PicYmax','PicZmin','PicZmax'])
        limits = np.array([
            limits['PicXmin'],limits['PicXmax'],
            limits['PicYmin'],limits['PicYmax'],
            limits['PicZmin'],limits['PicZmax'],
        ])
        if zlim is not None:
            limits[4:] = zlim
        return {
            'center': (limits[1::2]+limits[0::2])*0.5,
            'region': apy.coord.regionBox(limits)
        }
