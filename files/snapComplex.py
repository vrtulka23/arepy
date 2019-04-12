import numpy as np
import arepy as apy
from scipy.spatial import cKDTree

# This part calculates complex properties from simple properties
class snapComplex:
    def initComplex(self):
        self.cProps = ['RadHistogram','BoxProjection','BoxHistogram','BoxSlice','AngularMomentum','MassCenter',
                       'RadialRegion','BoxRegion','Histogram1D','Histogram2D','Maximum','Minimum','Mean','MinPos','Sum']

    def getPropertyComplex(self,prop,ids=None):
        name = prop['name']             # name of the property
        nproc = self.opt['nproc']       # number of processors that read a single snapshot
    
        if name=='RadHistogram':
            # Example: bins=np.linspace(1,10,1)
            #          {'name':'RadHistogram','p':'X_HP','center':[0.5,0.5,0.5],'bins':bins}
            region = {'name':'RadialRegion','center':prop['center'],'radius':prop['bins'][-1]}
            ids,r2 = self.getPropertyComplex(region,ids=ids)
            w = self.getPropertySimple(['Masses'],ids=ids)[0]
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
                    rids,r2 = self.getPropertyComplex({'name':'RadialRegion','ptype':pt,'transf':prop['transf']},ids=ids)
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
            region = {'name':'RadialRegion','center':prop['center'],'radius':prop['radius']}
            ids, r2 = self.getPropertyComplex(region,ids=ids)
            pos, mass, vel = self.getPropertySimple(['Coordinates','Masses','Velocities'],ids=ids)
            m, (x,y,z), (vx,vy,vz) = mass, (pos-prop['center']).T, vel.T
            Lx,Ly,Lz = np.sum([ m*(y*vz-z*vy), m*(z*vx-x*vz), m*(x*vy-y*vx) ],axis=1) # total angular momentum
            return [Lx,Ly,Lz]

        elif name=='BoxHistogram':
            # Example: {'name':'BoxHistogram','center':[0.5,0.5,0.5],'size':1,'w':'Masses','bins':200}
            box = apy.coord.box(prop['size'],prop['center'])
            bins = [ np.linspace(box[0],box[1],prop['bins']), np.linspace(box[0],box[1],prop['bins']) ]         
            region = {'name':'BoxRegion','box':box}
            ids,coord = self.getPropertyComplex(region,ids=ids)
            weights = self.getPropertySimple([prop['w']], ids=ids)[0]
            hist,xedges,yedges = np.histogram2d(coord[:,0], coord[:,1], bins=bins, weights=weights)
            return hist

        elif name=='BoxSlice':
            # Example: {'name':'BoxSlice','transf':transf,'w':'Density','bins':200,'n_jobs':1}
            transf = prop['transf']
            center = transf['select']['center']
            radius = transf['select']['radius']
            region = {'name':'RadialRegion','center':center,'radius':radius}
            ids,r2 = self.getPropertyComplex(region,ids=ids)
            coord = self.getPropertySimple(['Coordinates'],ids=ids)[0]

            # perform coordinate transformations
            coord = transf.convert(['translate','align','flip','rotate','crop'],coord)

            # initiate a grid
            box = transf['crop']['box']
            grid = apy.coord.grid( [prop['bins']]*2, box[:4], zfill=np.mean(box[4:]))

            # find s nearest neighbors to each grid point
            n_jobs = prop['n_jobs'] if 'n_jobs' in prop else 1
            kdt = cKDTree(coord,n_jobs=n_jobs)
            dist,pix = kdt.query(grid.coords)

            # select property
            properties = prop['w'] if isinstance(prop['w'],list) else [prop['w']]
            pps = self.getPropertySimple(properties,ids=ids)
            data = []
            for p,pp in enumerate(pps):
                pp = transf.select('crop',pp)
                data.append(pp[pix].reshape([prop['bins']]*2))

            return data if isinstance(prop['w'],list) else data[0]

        elif name=='BoxProjection':
            # Example: {'name':'BoxProjection','transf':transf,'w':'Density','bins':200,'n_jobs':1}
            if prop['transf'] is None:
                coord,mass = self.getPropertySimple(['Coordinates','Masses'])
            else:
                transf = prop['transf']
                center = transf['select']['center']
                radius = transf['select']['radius']
                region = {'name':'RadialRegion','center':center,'radius':radius}
                ids,r2 = self.getPropertyComplex(region,ids=ids)
                coord,mass = self.getPropertySimple(['Coordinates','Masses'],ids=ids)
            
                # perform coordinate transformations
                coord = transf.convert(['translate','align','flip','rotate','crop'],coord)
                mass = transf.select('crop',mass)            

            # initiate a grid
            if prop['transf'] is None:
                grid = apy.coord.grid( [prop['bins']]*3, transf['crop']['box'] )
            else:
                grid = apy.coord.grid( [prop['bins']]*3, transf['crop']['box'] )
            pix = grid.getPixFromCoord(coord)
            grid.addAtPix('num',pix,1)
            grid.addAtPix('mass',pix,mass)

            # locate empty and full pixels
            pixFull = grid.data['num']>0
            pixEmpty = grid.data['num']==0            
            coordFull = grid.grid[pixFull]
            coordEmpty = grid.grid[pixEmpty]
            massFull = grid.data['mass'][pixFull]

            # for each empty pixel find the closest full pixel
            kdt = cKDTree(coordFull)
            n_jobs = prop['n_jobs'] if 'n_jobs' in prop else 1
            dist,ngbEmpty = kdt.query(coordEmpty,n_jobs=n_jobs)
            numPix = np.full(pixFull.sum(),1,dtype=int)
            np.add.at(numPix,ngbEmpty,1)
            unitFullMass = massFull/numPix
            grid.data['mass'][pixFull] = unitFullMass
            grid.data['mass'][pixEmpty] = unitFullMass[ngbEmpty]

            # prepare projected properties
            properties = prop['w'] if isinstance(prop['w'],list) else [prop['w']]
            load = [pp for pp in properties if pp not in ['Masses','Density']]
            if len(load)>0:
                pps = self.getPropertySimple(load,ids=ids)
                for p,pp in enumerate(pps):
                    pp = transf.select('crop',pp)
                    ppk = 'pp%d'%p
                    grid.addAtPix(ppk,pix,pp*mass)
                    unitFullPP = grid.data[ppk][pixFull]/numPix
                    grid.data[ppk][pixFull] = unitFullPP
                    grid.data[ppk][pixEmpty] = unitFullPP[ngbEmpty]
 
            # return final data
            data,i = [],0
            for p,pp in enumerate(properties):
                mass = grid.data['mass'].sum(axis=2)
                if pp=='Masses':
                    projection = mass
                elif pp=='Density':
                    box = transf['crop']['box']
                    area = (box[1]-box[0])*(box[3]-box[2])
                    projection = mass / area * prop['bins']**2
                else:
                    ppk = 'pp%d'%i
                    projection = grid.data[ppk].sum(axis=2) / mass
                    i += 1
                data.append(projection)
            return data if isinstance(prop['w'],list) else data[0]

        elif name in ['RadialRegion','BoxRegion']:
            # Example: {'name':RadialRegion,'center':[0.5,0.5,0.5],'radius':0.5}
            if 'transf' in prop:
                select = prop['transf']['select']
                if name=='RadialRegion':
                    region = {'name':name,'center':select['center'],'radius':select['radius']}
                elif name=='BoxRegion':
                    region = {'name':name,'box':select['box']}
            else:
                region = prop
            data = self.getPropertySimple([region],ids=ids)[0]
            if nproc>1:
                prop0 = [ s[0] for s in data ]
                prop1 = [ s[1] for s in data ]
                return prop0, np.vstack(prop1) # we keep ids ordered by the file
            else:
                return data

        elif name in ['Histogram1D','Histogram2D']:
            data = self.getPropertySimple([prop],ids=ids)[0]
            return np.sum(data,axis=0) if nproc>1 else data

        elif name in ['Maximum','Minimum','Mean','MinPos','Sum']:
            data = self.getPropertySimple([prop],ids=ids)[0]         
            return np.array(data).flatten() if nproc>1 else data
