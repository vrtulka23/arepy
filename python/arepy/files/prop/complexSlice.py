import numpy as np
import arepy as apy

class complexSlice:
    """Box slices"""

    def _propBoxSlice(self,prop,grid,ids,ptype):
        import scipy.spatial as spatial

        transf = prop['transf']
        region = self.getProperty({
            'name':'RegionSphere', 'transf': transf,
            'p':['Indexes','Coordinates']},
        ids=ids,ptype=ptype)
        
        # Coordinate transformations
        # We do not crop our selection here, because sometimes the closest cells to the grid 
        # can be actually outside of the crop region
        coord = transf.convert(['translate','align','flip','rotate'],region['Coordinates'])
        points = grid.coords
            
        # find s nearest neighbors to each grid point
        properties = apy.files.properties(prop['w'])
        if len(coord)>0:
            # find the closest cells to the points
            kdt = spatial.cKDTree(coord)
            dist,pix = kdt.query(
                points,
                n_jobs = prop['n_jobs'] if 'n_jobs' in prop else 1
            )
            # select property
            load = properties.getWithout('name',['Coordinates','Bins'])
            pps = self.getProperty(load,ids=region['Indexes'],ptype=ptype,dictionary=True)
            for pp in properties:
                if pp['name']=='Coordinates':
                    properties.setData(pp['key'], grid.reshapeData(points))
                elif pp['name']=='Bins':
                    properties.setData(pp['key'], grid.xi )
                else:
                    ppSelected = pps[pp['key']]
                    reshaped = grid.reshapeData(ppSelected[pix])
                    if pp['name'] in ['Velocities']:  # flip field components if necessary
                        reshaped = transf.convert(['align','flip','rotate'],reshaped)
                    properties.setData(pp['key'], reshaped )
        else:
            apy.shell.warn('No cells in the selected region (propComplex.py)')
            print(transf['select']['region'].center,transf['select']['region'].radius)
            for pp in properties:
                properties.setData(pp['key'], None )
        return properties.getData()

    def prop_BoxPoints(self,ids,ptype,**prop):
        """Find property values for given points"""
        points = prop['transf'].convert(['translate','align','flip','rotate','crop'],prop['points'])
        # DEBUG: this needs to be converted to grid somehow
        return self._propBoxSlice(prop,points,ids,ptype)

    def prop_BoxLine(self,ids,ptype,**prop):
        """Find property values for a given line"""
        box = prop['transf']['crop']['region'].limits
        grid = apy.coord.gridLine(prop['bins'], box[:2], yfill=np.mean(box[2:4]), zfill=np.mean(box[4:]))
        return self._propBoxSlice(prop,grid,ids,ptype)

    def prop_BoxSquareXY(self,ids,ptype,**prop):
        """Find property values for a given XY sphere"""
        box = prop['transf']['crop']['region'].limits
        bins = [prop['bins']]*2 if np.isscalar(prop['bins']) else prop['bins']
        grid = apy.coord.gridSquareXY(bins, box[:4], zfill=np.mean(box[4:]))
        return self._propBoxSlice(prop,grid,ids,ptype)

    def prop_BoxFieldXY(self,ids,ptype,**prop):
        """Find property values for a given field"""
        box = prop['transf']['crop']['region'].limits
        grid = apy.coord.gridFieldXY([prop['bins']]*2, box[:4], zfill=np.mean(box[4:]))
        return self._propBoxSlice(prop,grid,ids,ptype)

    def prop_BoxLineRZ(self,ids,ptype,**prop):
        """Find property values for a RZ lines"""
        box = prop['transf']['crop']['region'].limits
        extent = [np.mean(box[0:2]), box[1], box[4], box[5]]
        grid = apy.coord.gridLineRZ([prop['bins'],prop['bins']*2], extent, xfill=np.mean(box[:2]), yfill=np.mean(box[2:4]))
        return self._propBoxSlice(prop,grid,ids,ptype)

    def prop_BoxLineXYZ(self,ids,ptype,**prop):
        """Find property values for a given XYZ line"""
        box = prop['transf']['crop']['region'].limits
        grid = apy.coord.gridLineXYZ([prop['bins']]*3, box, xfill=np.mean(box[:2]),
                                     yfill=np.mean(box[2:4]), zfill=np.mean(box[4:]))
        return self._propBoxSlice(prop,grid,ids,ptype)

    def prop_BoxHealpix(self,ids,ptype,**prop):
        """Find property values for a Healpix gird"""
        box = prop['transf']['crop']['region'].limits
        grid = apy.coord.gridHealpix(prop['bins'], box)
        return self._propBoxSlice(prop,grid,ids,ptype)
