import numpy as np
import arepy as apy
import h5py as hp

class simpleSelect:
    """Simple selections

    These function return selection indexes according to different selection criteria.

    Examples:
    
    1) Return selection together with other properties::

        >>> particleIDs = [20234939, 42394849, 2384784,...]
        >>> snap.getProperty([
        >>>      'ParticleIDs',
        >>>      {'name':'SelectIds', 'pids': particleIDs}
        >>> ])
        
        {'ParticleIDs': [20234939, 5234234, 94588239,...],
         'SelectIds': [True, False, False, ...]}
    
    2) Return selection only::

        >>> particleIDs = [20234939, 42394849, 2384784,...]
        >>> snap.getProperty({'name':'SelectIds', 'pids': particleIDs})
        
        [True, False, False, ...]

    """

    def prop_SelectIds(self,ids,ptype,**prop):
        """Select cells with particular IDs

        :param list[int] pids: Particle IDs
        :return: Selection indexes of the selected particles
        :rtype: list[int]

        .. note::
            For large numbers of IDs this can get quite slow, because it uses *numpy.in1d()* function.
        """
        idsSelect = np.in1d(self.prop_ParticleIDs(ids,ptype,**prop),prop['pids'])
        return np.where(ids, idsSelect, False)

    def prop_SelectSphere(self,ids,ptype,**prop): 
        """Select cells from a spherical region

        :param float radius: Sphere radius
        :param [float]*3 center: Sphere center
        :return: Selection indexes of the selected particles
        :rtype: list[int]
        """
        coord = self.prop_Coordinates(ids,ptype,**prop)-prop['center']
        r2 = coord[:,0]**2 + coord[:,1]**2 + coord[:,2]**2
        idsSelect = r2 < prop['radius']**2
        return np.where(ids, idsSelect, False)

    def prop_SelectBox(self,ids,ptype,**prop):    
        """Select cells from a box

        :param [float]*6 center: Box limits (xmin,xmax,ymin,ymax,zmin,zmax)
        :return: Selection indexes of the selected particles
        :rtype: list[int]
        """
        coord = np.array(self.prop_Coordinates(ids,ptype,**prop))
        box = np.array(prop['box'])
        idsSelect = (box[0]<coord[:,0]) & (coord[:,0]<box[1]) & \
                    (box[2]<coord[:,1]) & (coord[:,1]<box[3]) & \
                    (box[4]<coord[:,2]) & (coord[:,2]<box[5])
        return np.where(ids, idsSelect, False)

    def prop_SelectPoints(self,ids,ptype,**prop):
        """Select cells closest to the given points

        :param list[[float]*3] coord: List of coordinates
        :return: Selection indexes of the selected particles
        :rtype: list[int]
        """
        from scipy.spatial import cKDTree
        coord = self.prop_Coordinates(ids,ptype,**prop)
        grid = prop['coord']
        kdt = cKDTree(coord)
        dist,ids = kdt.query(grid)
        return ids

    def prop_Indexes(self,ids,ptype,**prop):
        """Get current selector indexes

        :return: Array with selector indexes
        :rtype: list[bool]
        """
        return ids
