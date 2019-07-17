import numpy as np
import arepy as apy

# This part calculates complex properties from simple properties
class snapComplex:

    ########################
    # Various
    ########################

    def propComplex_MassCenter(self,prop,ids=None):
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
                center = prop['transf']['select']['center']
                radius = prop['transf']['select']['radius']
                rids = self.getProperty({
                    'name':'RadialRegion','ptype':pt,'center':center,'radius':radius
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

    def propComplex_AngularMomentum(self,prop,ids=None):
        # Example: {'name':'AngularMomentum','center':[0.5,0.5,0.5],'radius':0.5}
        region = self.getProperty({
            'name':'RadialRegion','center':prop['center'],'radius':prop['radius'],
            'p': ['Coordinates','Masses','Velocities']
        },ids=ids)
        m, (x,y,z), (vx,vy,vz) = region['Masses'], (region['Coordinates']-prop['center']).T, region['Velocities'].T
        Lx,Ly,Lz = np.sum([ m*(y*vz-z*vy), m*(z*vx-x*vz), m*(x*vy-y*vx) ],axis=1) # total angular momentum
        return [Lx,Ly,Lz]

    def propComplex_VolumeFraction(self,prop,ids=None):
        # Volume fraction of the cells with some properties, relative to the selected region (ids)
        # Example: {'name':'VolumeFraction','p':'Mass','lt':1}
        volume = self.getProperty('CellVolume',ids=ids)
        properties = apy.files.snapProperties(prop['p'])
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

    def propComplex_RadHistogram(self,prop,ids=None):
        # Example: bins=np.linspace(1,10,1)
        #          {'name':'RadHistogram','p':'X_HP','center':[0.5,0.5,0.5],'bins':bins}
        region = self.getProperty({
            'name':'RadialRegion','center':prop['center'],'radius':prop['bins'][-1],'ptype':prop['ptype'],
            'p':[{'name':'Masses','ptype':prop['ptype']},{'name':'Radius2','center':prop['center']}]
        },ids=ids)
        wHist, edges = np.histogram(region['Radius2'],bins=prop['bins']**2,weights=region['Masses'],density=False)
        if isinstance(prop['p'],(str,dict)):
            p = self.getPropertySimple([prop['p']],ids=region['Indexes'])[0]
            pHist, edges = np.histogram(region['Radius2'],bins=prop['bins']**2,weights=region['Masses']*p,density=False)
            results = pHist/wHist
        else:
            p = self.getPropertySimple(prop['p'],ids=region['Indexes'])
            results = []
            for i in range(len(prop['p'])):
                pHist, edges = np.histogram(region['Radius2'],bins=prop['bins']**2,weights=region['Masses']*p[i],density=False)
                results.append( pHist/wHist )
        return results

    def propComplex_BoxHistogram(self,prop,ids=None):
        # Example: {'name':'BoxHistogram','center':[0.5,0.5,0.5],'size':1,'w':'Masses','bins':200}
        box = apy.coord.box(prop['size'],prop['center'])
        bins = [ np.linspace(box[0],box[1],prop['bins']), np.linspace(box[0],box[1],prop['bins']) ]         
        data = self.getProperty({
            'name':'BoxRegion','box':box,
            'p':['Coordinates',prop['w']]
        },ids=ids)
        weights = data[prop['w']] # actually here we shold select name of the prop['w'], but we are lazy!!!
        hist,xedges,yedges = np.histogram2d(data['Coordinates'][:,0], data['Coordinates'][:,1], bins=bins, weights=weights)
        return hist

    def _propHistogram(self,prop,ids=None):
        data = self.getPropertySimple([prop],ids=ids)[0]
        return np.sum(data,axis=0) if self.opt['nsub']>1 else data
    def propComplex_Histogram1D(self,prop,ids=None):
        return self._propHistogram(prop,ids)
    def propComplex_Histogram2D(self,prop,ids=None):
        return self._propHistogram(prop,ids)

    #######################
    # Box Slices
    #######################

    def _propBoxSlice(self,prop,grid,ids=None):
        import scipy.spatial as spatial

        # Example: {'name':'BoxSquareXY','transf':transf,'w':'Density','bins':200,'n_jobs':1}
        transf = prop['transf']
        center = transf['select']['center']
        radius = transf['select']['radius']
        region = self.getProperty({'name':'RadialRegion', 'center':center, 
                                   'radius':radius, 'p':'Coordinates'},ids=ids)
        
        # perform coordinate transformations
        coord = transf.convert(['translate','align','flip','rotate','crop'],region['Coordinates'])
        points = grid.coords
            
        # find s nearest neighbors to each grid point
        if len(coord)>0:
            kdt = spatial.cKDTree(coord)
            n_jobs = prop['n_jobs'] if 'n_jobs' in prop else 1
            dist,pix = kdt.query(points,n_jobs=n_jobs)

            # select property
            properties = apy.files.snapProperties(prop['w'])
            load = properties.getWithout('name',['Coordinates','Bins'])
            pps = self.getPropertySimple(load,ids=region['Indexes'])
            data = []
            for p,pp in enumerate(pps):
                pp = transf.select('crop',pp)
                reshaped = grid.reshapeData(pp[pix])
                if load[p]['name'] in ['Velocities']:  # flip field components if necessary
                    reshaped = transf.convert(['align','flip','rotate'],reshaped)
                data.append( reshaped )
            for p,pp in enumerate(properties):
                if pp['name']=='Coordinates':
                    data.insert(p, grid.reshapeData(points) )
                elif pp['name']=='Bins':
                    data.insert(p, grid.xi )
        else:
            properties = apy.files.snapProperties(prop['w'])
            data = [None for p in properties]

        return properties.results(data)

    def propComplex_BoxPoints(self,prop,ids=None):
        points = prop['transf'].convert(['translate','align','flip','rotate','crop'],prop['points'])
        # DEBUG: this needs to be converted to grid somehow
        return self._propBoxSlice(prop,points,ids)

    def propComplex_BoxLine(self,prop,ids=None):
        box = prop['transf']['crop']['box']
        grid = apy.coord.gridLine(prop['bins'], box[:2], yfill=np.mean(box[2:4]), zfill=np.mean(box[4:]))
        return self._propBoxSlice(prop,grid,ids)

    def propComplex_BoxSquareXY(self,prop,ids=None):
        box = prop['transf']['crop']['box']
        grid = apy.coord.gridSquareXY([prop['bins']]*2, box[:4], zfill=np.mean(box[4:]))
        return self._propBoxSlice(prop,grid,ids)

    def propComplex_BoxFieldXY(self,prop,ids=None):
        box = prop['transf']['crop']['box']
        grid = apy.coord.gridFieldXY([prop['bins']]*2, box[:4], zfill=np.mean(box[4:]))
        return self._propBoxSlice(prop,grid,ids)

    def propComplex_BoxLineRZ(self,prop,ids=None):
        box = prop['transf']['crop']['box']
        extent = [np.mean(box[0:2]), box[1], box[4], box[5]]
        grid = apy.coord.gridLineRZ([prop['bins'],prop['bins']*2], extent, xfill=np.mean(box[:2]), yfill=np.mean(box[2:4]))
        return self._propBoxSlice(prop,grid,ids)

    def propComplex_BoxLineXYZ(self,prop,ids=None):
        box = prop['transf']['crop']['box']
        grid = apy.coord.gridLineXYZ([prop['bins']]*3, box, xfill=np.mean(box[:2]),
                                     yfill=np.mean(box[2:4]), zfill=np.mean(box[4:]))
        return self._propBoxSlice(prop,grid,ids)

    def propComplex_BoxHealpix(self,prop,ids=None):
        grid = apy.coord.gridHealpix(prop['bins'], prop['transf']['crop']['box'])
        return self._propBoxSlice(prop,grid,ids)

    #####################
    # Box Projections
    #####################

    def propComplex_BoxProjCube(self,prop,ids=None):
        import scipy.spatial as spatial
        # Example: {'name':'BoxProjCube','transf':transf,'w':'Density','bins':200,'n_jobs':1}
        if prop['transf'] is None:
            coord,mass = self.getPropertySimple(['Coordinates','Masses'])
        else:
            transf = prop['transf']
            center = transf['select']['center']
            radius = transf['select']['radius']
            region = self.getProperty({
                'name':'RadialRegion','center':center,'radius':radius,
                'p':['Coordinates','Masses']
            },ids=ids)
            
            # perform coordinate transformations
            coord = transf.convert(['translate','align','flip','rotate','crop'],region['Coordinates'])
            mass = transf.select('crop',region['Masses'])            
            ids = region['Indexes']

        # load and crop projected properties
        properties = apy.files.snapProperties(prop['w'])
        load = properties.getWithout('name',['Masses','Density'])
        if len(load)>0:
            pps = self.getPropertySimple(load,ids=ids)
            pps = [transf.select('crop',pp) for pp in pps]

        # initiate a grid
        if prop['transf'] is None:  # TODO: this case need to be edited
            grid = apy.coord.gridCube([prop['bins']]*3, transf['crop']['box'] )
        else:
            grid = apy.coord.gridCube([prop['bins']]*3, transf['crop']['box'] )

        pix = grid.getPixFromCoord(coord)
        grid.addAtPix('num',pix,1)
        grid.addAtPix('mass',pix,mass)
        
        # locate empty and full pixels
        pixFull = grid.data['num']>0
        pixEmpty = grid.data['num']==0            
        coordFull = grid[pixFull]
        coordEmpty = grid[pixEmpty]
        massFull = grid.data['mass'][pixFull]
        
        # for each empty pixel find the closest full pixel
        kdt = spatial.cKDTree(coordFull)
        
        n_jobs = prop['n_jobs'] if 'n_jobs' in prop else 1
        dist,ngbEmpty = kdt.query(coordEmpty,n_jobs=n_jobs)
        
        numPix = np.full(pixFull.sum(),1,dtype=int)
        np.add.at(numPix,ngbEmpty,1)
        unitFullMass = massFull/numPix
        grid.data['mass'][pixFull] = unitFullMass
        grid.data['mass'][pixEmpty] = unitFullMass[ngbEmpty]
        
        # prepare projected properties
        if len(load)>0:
            for p,pp in enumerate(pps):
                ppk = 'pp%d'%p
                grid.addAtPix(ppk,pix,pp*mass)
                unitFullPP = grid.data[ppk][pixFull]/numPix
                grid.data[ppk][pixFull] = unitFullPP
                grid.data[ppk][pixEmpty] = unitFullPP[ngbEmpty]

        # return final data
        data,i = [],0
        for p,pp in enumerate(properties):
            mass = grid.data['mass'].sum(axis=2)
            if pp['name']=='Masses':
                projection = mass
            elif pp['name']=='Density':
                box = transf['crop']['box']
                area = (box[1]-box[0])*(box[3]-box[2])
                projection = mass / area * prop['bins']**2
            else:
                ppk = 'pp%d'%i
                projection = grid.data[ppk].sum(axis=2) / mass
                i += 1
            data.append(projection)
            
        return properties.results(data)

    ######################
    # Coordinate Regions
    ######################

    def propComplex_GridRegion(self,prop,ids=None):
        # Example: {'name':'GridRegion','grid':grid}
        data = self.getPropertySimple([prop],ids=ids)[0]
        if self.opt['nsub']>1:
            apy.shell.exit('This feature neetds to be implemented (snapComplex.py)')
        else:
            return [data[i] for i in range(1,len(data))] # remove dist parameter
            
    def _propRegion(self,prop,ids=None):
        # Example: {'name':'RadialRegion','center':[0.5,0.5,0.5],'radius':0.5}
        # Example: {'name':'BoxRegion','box':[0,1,0,1,0,1]}
        data = self.getPropertySimple([prop],ids=ids)[0]
        if 'p' in prop:
            properties = apy.files.snapProperties('Indexes')
            properties.add(prop['p'])
            if self.opt['nsub']>1:
                rdata = [ [ s[0] for s in data ] ]
                for p in range(1,len(data[0])):
                    if np.ndim(data[0][p])>1:  # in case of coordinates, rates,...
                        d = np.vstack([ s[p] for s in data ])
                    else:                      # in case of masses, ids,...
                        d = np.hstack([ s[p] for s in data ])
                    rdata.append( d )
                data = rdata
            return properties.results(data)
        else:
            return data # otherwise return only indexes
    def propComplex_RadialRegion(self,prop,ids=None):
        return self._propRegion(prop,ids)
    def propComplex_BoxRegion(self,prop,ids=None):
        return self._propRegion(prop,ids)
    def propComplex_IDsRegion(self,prop,ids=None):
        return self._propRegion(prop,ids)

    def propComplex_ConeRegion(self,prop,ids=None):
        transf = prop['transf']
        center = transf['select']['center']
        radius = transf['select']['radius']
        region = self.getProperty({'name':'RadialRegion','center':center,'radius':radius,'p':'Coordinates'},ids=ids)

        # transform coordinates and indexes
        region['Coordinates'] = transf.convert(['translate','align','flip','rotate','crop'],region['Coordinates'])
        idTrue = np.where(region['Indexes'])[0]   
        region['Indexes'][idTrue] = transf.items['crop']['ids'] 

        # get all data and return
        properties = apy.files.snapProperties('Indexes')
        if 'p' in prop:
            properties = apy.files.snapProperties(prop['p'])
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
        

    ###############################
    # Property statistics
    ###############################

    def _propStats(self,prop,ids=None):
        data = self.getPropertySimple([prop],ids=ids)[0]         
        # if there are more snapshot sub-files, return separate results for each
        return np.array(data).flatten() if self.opt['nsub']>1 else data 
    def propComplex_Maximum(self,prop,ids=None):
        return self._propStats(prop,ids)
    def propComplex_Minimum(self,prop,ids=None):
        return self._propStats(prop,ids)
    def propComplex_Mean(self,prop,ids=None):
        return self._propStats(prop,ids)
    def propComplex_MinPos(self,prop,ids=None):
        return self._propStats(prop,ids)
    def propComplex_Sum(self,prop,ids=None):
        return self._propStats(prop,ids)
