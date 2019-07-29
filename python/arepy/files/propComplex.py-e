import numpy as np
import arepy as apy

# This part calculates complex properties from simple properties
class propComplex:

    ########################
    # Various
    ########################

    def prop_MassCenter(self,prop,ids):
        # Example: {'name':'MassCenter','transf':transf,'ptype':[0,1]}
        if 'ptype' in prop:
            pts = [prop['ptype']] if np.isscalar(prop['ptype']) else prop['ptype']
        else:
            pts = range(6)
        npart = self.getHeader('NumPart_Total')
        npartsum = np.sum(npart[pts])
        data = apy.data.collector()
        for i,pt in enumerate(pts):
            if npart[pt]==0: continue
            if 'transf' in prop and 'select' in prop['transf'].items:
                rids = self.getProperty({
                    'name':'RegionSphere','ptype':pt,'transf':prop['transf'],
                },ids=ids)
            else: 
                rids = ids
            rdata = self.getProperty([
                {'name':'Masses','ptype':pt},
                {'name':'Coordinates','ptype':pt}
            ],ids=rids)
            data.add(i,npartsum,len(rdata['Masses']),{
                'xweight': rdata['Coordinates'][:,0] * rdata['Masses'],
                'yweight': rdata['Coordinates'][:,1] * rdata['Masses'],
                'zweight': rdata['Coordinates'][:,2] * rdata['Masses'],
                'mass':    rdata['Masses'],
            })
        if len(data)>0:
            center = np.array([ np.sum(data['xweight']), np.sum(data['yweight']), np.sum(data['zweight']) ]) 
            center /= np.sum(data['mass'])
            if 'transf' in prop:
                center = prop['transf'].convert(['translate','align','flip','rotate','crop'],center)
            return center
        else:
            return [np.nan]*3

    def prop_AngularMomentum(self,prop,ids):
        # Example: {'name':'AngularMomentum','center':[0.5,0.5,0.5],'radius':0.5}
        region = self.getProperty({
            'name':'RegionSphere','center':prop['center'],'radius':prop['radius'],
            'p': ['Coordinates','Masses','Velocities']
        },ids=ids)
        m, (x,y,z), (vx,vy,vz) = region['Masses'], (region['Coordinates']-prop['center']).T, region['Velocities'].T
        Lx,Ly,Lz = np.sum([ m*(y*vz-z*vy), m*(z*vx-x*vz), m*(x*vy-y*vx) ],axis=1) # total angular momentum
        return [Lx,Ly,Lz]

    def prop_VolumeFraction(self,prop,ids):
        # Volume fraction of the cells with some properties, relative to the selected region (ids)
        # Example: {'name':'VolumeFraction','p':'Mass','lt':1}
        volume = self.getProperty('CellVolume',ids=ids)
        properties = apy.files.properties(prop['p'])
        data = self.getProperty(properties,ids=ids)
        volTot = np.sum(volume)
        ids = [True]*len(volume)
        if 'lt' in prop: # larger than
            ids = ids & (data>prop['lt'])
        if 'st' in prop: # smaller than
            ids = ids & (data<prop['st'])
        return np.sum(volume[ids])/volTot            

    #######################
    # Histograms
    #######################

    def prop_HistSphere(self,prop,ids):
        # Example: bins=np.linspace(1,10,1)
        #          {'name':'HistSphere','p':'X_HP','center':[0.5,0.5,0.5],'bins':bins}
        region = self.getProperty({
            'name':'RegionSphere','center':prop['center'],'radius':prop['bins'][-1],'ptype':prop['ptype'],
            'p':['Indexes',{'name':'Masses','ptype':prop['ptype']},{'name':'Radius2','center':prop['center']}]
        },ids=ids)
        wHist, edges = np.histogram(region['Radius2'],bins=prop['bins']**2,weights=region['Masses'],density=False)

        properties = apy.files.properties(prop['p'])
        data = self.getProperty(properties,ids=region['Indexes'],dictionary=True)
        for pp in properties:
            pHist, edges = np.histogram(region['Radius2'],bins=prop['bins']**2,
                                        weights=region['Masses']*data[pp['key']],density=False)
            properties.setData(pp['key'], pHist/wHist)
        return properties.getData()

    def prop_HistBox(self,prop,ids):
        # Example: {'name':'HistBox','center':[0.5,0.5,0.5],'size':1,'w':'Masses','bins':200}
        box = apy.coord.box(prop['size'],prop['center'])
        bins = [ np.linspace(box[0],box[1],prop['bins']), np.linspace(box[0],box[1],prop['bins']) ]         
        properties = apy.files.properties(['Coordinates',prop['w']])
        data = self.getProperty({'name':'RegionBox','box':box,'p':properties},ids=ids)
        hist,xedges,yedges = np.histogram2d(data['Coordinates'][:,0], data['Coordinates'][:,1], 
                                            bins=bins, weights=data[properties[1]['key']])
        return hist

    #######################
    # Box Slices
    #######################

    # Example: {'name':'BoxSquareXY','transf':transf,'w':'Density','bins':200,'n_jobs':1}
    def _propBoxSlice(self,prop,grid,ids):
        import scipy.spatial as spatial

        transf = prop['transf']
        region = self.getProperty({
            'name':'RegionSphere', 'transf': transf,
            'p':['Indexes','Coordinates']},
        ids=ids)
        
        # perform coordinate transformations
        coord = transf.convert(['translate','align','flip','rotate','crop'],region['Coordinates'])
        points = grid.coords
            
        # find s nearest neighbors to each grid point
        properties = apy.files.properties(prop['w'])
        if len(coord)>0:
            kdt = spatial.cKDTree(coord)
            n_jobs = prop['n_jobs'] if 'n_jobs' in prop else 1
            dist,pix = kdt.query(points,n_jobs=n_jobs)

            # select property
            load = properties.getWithout('name',['Coordinates','Bins'])
            pps = self.getProperty(load,ids=region['Indexes'],dictionary=True)
            for pp in properties:
                if pp['name']=='Coordinates':
                    properties.setData(pp['key'], grid.reshapeData(points))
                elif pp['name']=='Bins':
                    properties.setData(pp['key'], grid.xi )
                else:
                    ppSelected = transf.select('crop',pps[pp['key']])
                    reshaped = grid.reshapeData(ppSelected[pix])
                    if pp['name'] in ['Velocities']:  # flip field components if necessary
                        reshaped = transf.convert(['align','flip','rotate'],reshaped)
                    properties.setData(pp['key'], reshaped )
        else:
            for pp in properties:
                properties.setData(pp['key'], None )
        return properties.getData()

    def prop_BoxPoints(self,prop,ids):
        points = prop['transf'].convert(['translate','align','flip','rotate','crop'],prop['points'])
        # DEBUG: this needs to be converted to grid somehow
        return self._propBoxSlice(prop,points,ids)

    def prop_BoxLine(self,prop,ids):
        box = prop['transf']['crop']['box']
        grid = apy.coord.gridLine(prop['bins'], box[:2], yfill=np.mean(box[2:4]), zfill=np.mean(box[4:]))
        return self._propBoxSlice(prop,grid,ids)

    def prop_BoxSquareXY(self,prop,ids):
        box = prop['transf']['crop']['box']
        grid = apy.coord.gridSquareXY([prop['bins']]*2, box[:4], zfill=np.mean(box[4:]))
        return self._propBoxSlice(prop,grid,ids)

    def prop_BoxFieldXY(self,prop,ids):
        box = prop['transf']['crop']['box']
        grid = apy.coord.gridFieldXY([prop['bins']]*2, box[:4], zfill=np.mean(box[4:]))
        return self._propBoxSlice(prop,grid,ids)

    def prop_BoxLineRZ(self,prop,ids):
        box = prop['transf']['crop']['box']
        extent = [np.mean(box[0:2]), box[1], box[4], box[5]]
        grid = apy.coord.gridLineRZ([prop['bins'],prop['bins']*2], extent, xfill=np.mean(box[:2]), yfill=np.mean(box[2:4]))
        return self._propBoxSlice(prop,grid,ids)

    def prop_BoxLineXYZ(self,prop,ids):
        box = prop['transf']['crop']['box']
        grid = apy.coord.gridLineXYZ([prop['bins']]*3, box, xfill=np.mean(box[:2]),
                                     yfill=np.mean(box[2:4]), zfill=np.mean(box[4:]))
        return self._propBoxSlice(prop,grid,ids)

    def prop_BoxHealpix(self,prop,ids):
        box = prop['transf']['crop']['box']
        grid = apy.coord.gridHealpix(prop['bins'], box)
        return self._propBoxSlice(prop,grid,ids)

    #####################
    # Box Projections
    #####################

    def prop_BoxProjCube(self,prop,ids):
        import scipy.spatial as spatial
        # Example: {'name':'BoxProjCube','transf':transf,'w':'Density','bins':200,'n_jobs':1}
        if prop['transf'] is None:
            region = self.getProperty(['Indexes','Coordinates','Masses'], ids=ids)
        else:
            transf = prop['transf']
            region = self.getProperty({
                'name':'RegionSphere','transf':transf, 
                'p':['Indexes','Coordinates','Masses']
            }, ids=ids)
            
            # perform coordinate transformations
            region['Coordinates'] = transf.convert(['translate','align','flip','rotate','crop'],region['Coordinates'])
            region['Masses'] = transf.select('crop',region['Masses'])            

        # load and crop projected properties
        properties = apy.files.properties(prop['w'])
        load = properties.getWithout('name',['Masses','Density'])
        if len(load)>0:
            data = self.getProperty(load, ids=region['Indexes'], dictionary=True)
            for pp in load:
                data[pp['key']] = transf.select('crop',data[pp['key']])

        # initiate a grid
        if prop['transf'] is None:  # TODO: this case need to be edited
            grid = apy.coord.gridCube([prop['bins']]*3, transf['crop']['box'] )
        else:
            grid = apy.coord.gridCube([prop['bins']]*3, transf['crop']['box'] )

        pix = grid.getPixFromCoord(region['Coordinates'])
        grid.addAtPix('num',pix,1)
        grid.addAtPix('mass',pix,region['Masses'])
        
        # locate empty and full pixels
        pixFull = grid.data['num']>0
        pixEmpty = grid.data['num']==0            
        coordFull = grid[pixFull]
        coordEmpty = grid[pixEmpty]
        massFull = grid.data['mass'][pixFull]
        
        # for each empty pixel find the closest full pixel
        kdt = spatial.cKDTree(coordFull)
        n_jobs = prop['n_jobs'] if 'n_jobs' in prop else 1
        dist,ngbFull = kdt.query(coordEmpty,n_jobs=n_jobs)
        
        # redistribute masses from full to their neighbor empty pixels
        numPix = np.full(pixFull.sum(),1,dtype=int)
        np.add.at(numPix,ngbFull,1)
        unitFullMass = massFull/numPix
        grid.data['mass'][pixFull] = unitFullMass
        grid.data['mass'][pixEmpty] = unitFullMass[ngbFull]
        
        # return final data
        for p,pp in enumerate(properties):
            massColumn = grid.data['mass'].sum(axis=2)
            if pp['name']=='Masses':
                projection = massColumn
            elif pp['name']=='Density':
                box = transf['crop']['box']
                area = (box[1]-box[0])*(box[3]-box[2])
                projection = massColumn / area * prop['bins']**2
            else:
                ppk = pp['key'] 
                grid.addAtPix(ppk, pix, data[ppk]*region['Masses'])
                unitFullPP = grid.data[ppk][pixFull]/numPix
                grid.data[ppk][pixFull] = unitFullPP
                grid.data[ppk][pixEmpty] = unitFullPP[ngbFull]
                projection = grid.data[ppk].sum(axis=2) / massColumn
            properties.setData(pp['key'],projection)
            
        return properties.getData()

    ######################
    # Coordinate Regions
    ######################

    # Example: {'name':'RegionSphere','center':[0.5,0.5,0.5],'radius':0.5}
    # Example: {'name':'RegionBox','box':[0,1,0,1,0,1]}
    def _propRegion(self,prop,ids):
        if 'p' in prop:
            # return properties in the selected region
            properties = apy.files.properties(prop['p'])
            del prop['p']
            region = self.getProperty(prop, ids=ids)
            return self.getProperty(properties, ids=region)
        else:
            # otherwise return only indexes
            return self.getProperty(prop, ids=ids) 
    def prop_RegionSphere(self,prop,ids):
        prop['name'] = 'SelectSphere'
        if 'transf' in prop:
            prop['center'] = prop['transf']['select']['center']
            prop['radius'] = prop['transf']['select']['radius']
        return self._propRegion(prop,ids)
    def prop_RegionBox(self,prop,ids):
        prop['name'] = 'SelectBox'
        if 'transf' in prop:
            prop['box'] = prop['transf']['select']['box']
        return self._propRegion(prop,ids)
    def prop_RegionIds(self,prop,ids):
        prop['name'] = 'SelectIds'
        return self._propRegion(prop,ids)
    def prop_RegionPoints(self,prop,ids):
        prop['name'] = 'SelectPoints'
        return self._propRegion(prop,ids)
            
    def prop_RegionCone(self,prop,ids):
        # select a spherical region
        transf = prop['transf']
        region = self.getProperty({
            'name':'RegionSphere','transf':transf,
            'p':['Indexes','Coordinates']},
        ids=ids)

        # transform coordinates and indexes and cut out a cone
        region['Coordinates'] = transf.convert(['translate','align','flip','rotate','crop'],region['Coordinates'])
        idTrue = np.where(region['Indexes'])[0]   
        region['Indexes'][idTrue] = transf.items['crop']['ids'] 

        # get all data and return
        if 'p' in prop:
            properties = apy.files.properties(prop['p'])
            rprops = properties.getWithout('key',['Indexes','Coordinates'])
            rdata = self.getProperty(rprops,ids=region['Indexes'],dictionary=True)
            for pp in properties:
                if pp['key']=='Indexes':
                    properties.setData('Indexes',region['Indexes'])
                elif pp['key']=='Coordinates':
                    properties.setData('Coordinates',region['Coordinates'])
                else:
                    properties.setData(pp['key'], rdata[pp['key']])
            return properties.getData()
        else:
            return region['Indexes']
        
