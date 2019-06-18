import numpy as np
import arepy as apy

# This part calculates complex properties from simple properties
class snapComplex:
    def initComplex(self):
        self.cProps = ['RadHistogram','BoxHistogram',
                       'BoxPoints','BoxSquareXY','BoxFieldXY','BoxHealpix',
                       'BoxLine','BoxLineRZ','BoxLineXYZ',
                       'BoxProjCube','BoxProjCylinder',
                       'AngularMomentum','MassCenter',
                       'RadialRegion','BoxRegion','IDsRegion',
                       'Histogram1D','Histogram2D',
                       'Maximum','Minimum','Mean','MinPos','Sum']

    def getPropertyComplex(self,prop,ids=None):
        import scipy.spatial as spatial

        name = prop['name']         # name of the property
        nproc = self.opt['nproc']   # number of processors that read a single snapshot
        nsub = self.opt['nsub']     # number of sub files for each snapshot
        if 'ptype' not in prop:
            prop['ptype'] = 0

        if name=='RadHistogram':
            # Example: bins=np.linspace(1,10,1)
            #          {'name':'RadHistogram','p':'X_HP','center':[0.5,0.5,0.5],'bins':bins}
            ids,w,r2 = self.getPropertyComplex({
                'name':'RadialRegion','center':prop['center'],'radius':prop['bins'][-1],'ptype':prop['ptype'],
                'p':[{'name':'Masses','ptype':prop['ptype']},{'name':'Radius2','center':prop['center']}]
            },ids=ids)
            wHist, edges = np.histogram(r2,bins=prop['bins']**2,weights=w,density=False)
            if isinstance(prop['p'],(str,dict)):
                p = self.getPropertySimple([prop['p']],ids=ids)[0]
                pHist, edges = np.histogram(r2,bins=prop['bins']**2,weights=w*p,density=False)
                results = pHist/wHist
            else:
                p = self.getPropertySimple(prop['p'],ids=ids)
                results = []
                for i in range(len(prop['p'])):
                    pHist, edges = np.histogram(r2,bins=prop['bins']**2,weights=w*p[i],density=False)
                    results.append( pHist/wHist )
            return results

        elif name=='MassCenter':
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
                    rids = self.getPropertyComplex({
                        'name':'RadialRegion','ptype':pt,'center':center,'radius':radius
                    },ids=ids)
                else: 
                    rids = ids
                mass,coord = self.getPropertySimple([
                    {'name':'Masses','ptype':pt},
                    {'name':'Coordinates','ptype':pt}
                ],ids=rids)
                data.add(i,npartsum,len(mass),{
                    'xweight': coord[:,0] * mass,
                    'yweight': coord[:,1] * mass,
                    'zweight': coord[:,2] * mass,
                    'mass':    mass,
                })
            if len(data)>0:
                center = np.array([ np.sum(data['xweight']), np.sum(data['yweight']), np.sum(data['zweight']) ]) 
                center /= np.sum(data['mass'])
                if 'transf' in prop:
                    center = prop['transf'].convert(['translate','align','flip','rotate','crop'],center)
                return center
            else:
                return [np.nan]*3

        elif name=='AngularMomentum':
            # Example: {'name':'AngularMomentum','center':[0.5,0.5,0.5],'radius':0.5}
            ids, pos, mass, vel = self.getPropertyComplex({
                'name':'RadialRegion','center':prop['center'],'radius':prop['radius'],
                'p': ['Coordinates','Masses','Velocities']
            },ids=ids)
            m, (x,y,z), (vx,vy,vz) = mass, (pos-prop['center']).T, vel.T
            Lx,Ly,Lz = np.sum([ m*(y*vz-z*vy), m*(z*vx-x*vz), m*(x*vy-y*vx) ],axis=1) # total angular momentum
            return [Lx,Ly,Lz]

        elif name=='BoxHistogram':
            # Example: {'name':'BoxHistogram','center':[0.5,0.5,0.5],'size':1,'w':'Masses','bins':200}
            box = apy.coord.box(prop['size'],prop['center'])
            bins = [ np.linspace(box[0],box[1],prop['bins']), np.linspace(box[0],box[1],prop['bins']) ]         
            ids,coord,weights = self.getPropertyComplex({
                'name':'BoxRegion','box':box,
                'p':['Coordinates',prop['w']]
            },ids=ids)
            hist,xedges,yedges = np.histogram2d(coord[:,0], coord[:,1], bins=bins, weights=weights)
            return hist

        elif name in ['BoxPoints','BoxLine','BoxSquareXY','BoxFieldXY','BoxLineRZ','BoxLineXYZ','BoxHealpix']:
            # Example: {'name':'BoxSquareXY','transf':transf,'w':'Density','bins':200,'n_jobs':1}
            transf = prop['transf']
            center = transf['select']['center']
            radius = transf['select']['radius']
            ids,coord = self.getPropertyComplex({
                'name':'RadialRegion','center':center,'radius':radius,
                'p':'Coordinates'
           },ids=ids)

            # perform coordinate transformations
            coord = transf.convert(['translate','align','flip','rotate','crop'],coord)

            # initiate a grid points
            box = transf['crop']['box']
            if name=='BoxPoints':     # uses arbitrary grid points within the whole volume
                points = transf.convert(['translate','align','flip','rotate','crop'],prop['points'])
            elif name=='BoxLine':     # creates line grid points on the x axis
                grid = apy.coord.gridLine(prop['bins'], box[:2], yfill=np.mean(box[2:4]), zfill=np.mean(box[4:]))
            elif name=='BoxSquareXY': # creates surface grid points on the x/y plane
                grid = apy.coord.gridSquareXY([prop['bins']]*2, box[:4], zfill=np.mean(box[4:]))
            elif name=='BoxFieldXY':  # get field vectors on the x/y plane
                grid = apy.coord.gridFieldXY([prop['bins']]*2, box[:4], zfill=np.mean(box[4:]))
            elif name=='BoxLineRZ':   # calculate R/Z line profiles
                extent = [np.mean(box[0:2]), box[1], box[4], box[5]]
                grid = apy.coord.gridLineRZ([prop['bins'],prop['bins']*2], extent, xfill=np.mean(box[:2]), yfill=np.mean(box[2:4]))
            elif name=='BoxLineXYZ':  # calculate X/Y/Z line profiles
                grid = apy.coord.gridLineXYZ([prop['bins']]*3, box, xfill=np.mean(box[:2]),
                                            yfill=np.mean(box[2:4]), zfill=np.mean(box[4:]))
            elif name=='BoxHealpix':  # calculate Healpix surface
                grid = apy.coord.gridHealpix(prop['bins'], box)
            points = grid.coords
            
            # find s nearest neighbors to each grid point
            if len(coord)>0:
                kdt = spatial.cKDTree(coord)
                n_jobs = prop['n_jobs'] if 'n_jobs' in prop else 1
                dist,pix = kdt.query(points,n_jobs=n_jobs)

                # select property
                properties = apy.files.snapProperties(prop['w'])
                load = properties.without('name',['Coordinates','Bins'])
                pps = self.getPropertySimple(load,ids=ids)
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

        elif name=='BoxProjCube':
            # Example: {'name':'BoxProjCube','transf':transf,'w':'Density','bins':200,'n_jobs':1}
            if prop['transf'] is None:
                coord,mass = self.getPropertySimple(['Coordinates','Masses'])
            else:
                transf = prop['transf']
                center = transf['select']['center']
                radius = transf['select']['radius']
                ids,coord,mass = self.getPropertyComplex({
                    'name':'RadialRegion','center':center,'radius':radius,
                    'p':['Coordinates','Masses']
                },ids=ids)

                # perform coordinate transformations
                coord = transf.convert(['translate','align','flip','rotate','crop'],coord)
                mass = transf.select('crop',mass)            

            # load and crop projected properties
            properties = apy.files.snapProperties(prop['w'])
            load = properties.without('name',['Masses','Density'])
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

        elif name=='GridRegion':
            # Example: {'name':'GridRegion','grid':grid}
            data = self.getPropertySimple([prop],ids=ids)[0]
            if nsub>1:
                apy.shell.exit('This feature neetds to be implemented (snapComplex.py)')
            else:
                return [data[i] for i in range(1,len(data))] # remove dist parameter
            
        elif name in ['RadialRegion','BoxRegion','IDsRegion']:
            # Example: {'name':'RadialRegion','center':[0.5,0.5,0.5],'radius':0.5}
            # Example: {'name':'BoxRegion','box':[0,1,0,1,0,1]}
            data = self.getPropertySimple([prop],ids=ids)[0]
            if nsub>1 and 'p' in prop:
                rdata = [ [ s[0] for s in data ] ]
                for p in range(1,len(data[0])):
                    if np.ndim(data[0][p])>1:  # in case of coordinates, rates,...
                        d = np.vstack([ s[p] for s in data ])
                    else:                      # in case of masses, ids,...
                        d = np.hstack([ s[p] for s in data ])
                    rdata.append( d )
                return rdata
            else:
                return data

        elif name in ['Histogram1D','Histogram2D']:
            data = self.getPropertySimple([prop],ids=ids)[0]
            return np.sum(data,axis=0) if nsub>1 else data

        elif name in ['Maximum','Minimum','Mean','MinPos','Sum']:
            data = self.getPropertySimple([prop],ids=ids)[0]         
            return np.array(data).flatten() if nsub>1 else data
