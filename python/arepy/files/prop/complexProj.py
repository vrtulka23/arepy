import numpy as np
import arepy as apy

class complexProj:
    """Projection image of a property"""

    def prop_BoxProjCube(self,ids,ptype,**prop):
        """Weighted projection of a property within a cube"""
        import scipy.spatial as spatial
        if prop['transf'] is None:
            region = self.getProperty(['Indexes','Coordinates','Masses'], ids=ids,ptype=ptype)
        else:
            transf = prop['transf']
            region = self.getProperty({
                'name':'RegionSphere',
                'center': transf['select']['region'].center,
                'radius': transf['select']['region'].radius,
                'p':['Indexes','Coordinates','Masses','CellVolume']
            }, ids=ids,ptype=ptype)
            
            # perform coordinate transformations
            coordInside = transf.convert(['translate','align','flip','rotate','crop'],region['Coordinates'])
            massInside = transf.select('crop',region['Masses'])

        # load and crop projected properties
        properties = apy.files.properties(prop['p'])
        load = properties.getWithout('name',['Masses','Density'])
        if len(load)>0:
            data = self.getProperty(load, ids=region['Indexes'], ptype=ptype, dictionary=True)
            for pp in load:
                data[pp['key']] = transf.select('crop',data[pp['key']])

        # initiate a grid
        if prop['transf'] is None:  # TODO: this case need to be edited
            grid = apy.coord.gridCube([prop['bins']]*3, transf['crop']['region'].limits )
        else:
            grid = apy.coord.gridCube([prop['bins']]*3, transf['crop']['region'].limits )

        pix = grid.getPixFromCoord(coordInside)
        grid.addAtPix('num',pix,1)
        grid.addAtPix('mass',pix,massInside)
        
        # locate empty and full pixels
        pixFull = grid.data['num']>0
        pixEmpty = grid.data['num']==0            
        coordFull = grid[pixFull]
        coordEmpty = grid[pixEmpty]
        massFull = grid.data['mass'][pixFull]

        numFull = pixFull.sum()
        
        # for each empty pixel find the closest full pixel
        kdt = spatial.cKDTree(coordFull)
        n_jobs = prop['n_jobs'] if 'n_jobs' in prop else 1
        dist,ngbFull = kdt.query(coordEmpty,n_jobs=n_jobs)

        # redistribute masses from full to their neighbor empty pixels
        numPix = np.full(numFull,1,dtype=int)
        np.add.at(numPix,ngbFull,1)
        unitFullMass = massFull/numPix
        grid.data['mass'][pixFull] = unitFullMass
        grid.data['mass'][pixEmpty] = unitFullMass[ngbFull]
        
        # return final data
        for p,pp in enumerate(properties):
            masscolumn = grid.data['mass'].sum(axis=2)
            if pp['name']=='Masses':
                projection = masscolumn
            elif pp['name']=='Density':
                box = transf['crop']['region'].limits
                area = (box[1]-box[0])*(box[3]-box[2])
                projection = masscolumn / area * prop['bins']**2  # this is a surface density in cm^-2
            else:  # these are mean values in the column
                ppk = pp['key'] 
                grid.addAtPix(ppk, pix, data[ppk]*massInside)
                unitFullPP = grid.data[ppk][pixFull]/numPix
                grid.data[ppk][pixFull] = unitFullPP
                grid.data[ppk][pixEmpty] = unitFullPP[ngbFull]
                projection = grid.data[ppk].sum(axis=2) / masscolumn
            properties.setData(pp['key'],projection)
            
        return properties.getData()
