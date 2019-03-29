import numpy as np
import arepy as apy

# This part calculates complex properties from simple properties
class snapComplex:

    def getPropertyComplex(self,ptype,prop,ids=None):
        name = prop['name']
        if name=='RadHistogram':
            # Example: bins=np.linspace(1,10,1)
            #          {'name':'RadHistogram','p':'X_HP','center':[0.5,0.5,0.5],'bins':bins}
            region = {'name':'SphericalRegion','center':prop['center'],'radius':prop['bins'][-1]}
            ids,r2 = self.getPropertySimple(0,[region],ids)[0]
            w = self.getPropertySimple(0,['Masses'],ids=ids)[0]
            p = self.getPropertySimple(0,prop['p'],ids=ids)
            wHist, edges = np.histogram(r2,bins=prop['bins']**2,weights=w)
            if isinstance(prop['p'],(str,dict)):
                pHist, edges = np.histogram(r2,bins=prop['bins']**2,weights=w*p)
                results = pHist/wHist
            else:
                results = []
                for i in range(len(prop['p'])):
                    pHist, edges = np.histogram(r2,bins=prop['bins']**2,weights=w*p[i])
                    results.append( pHist/wHist )
            return results

        elif name=='BoxHistogram':
            # Example: {'name':'BoxHistogram','center':[0.5,0.5,0.5],'size':1,'w':'Masses','bins':200}
            box = apy.coord.box(prop['size'],prop['center'])
            bins = [ np.linspace(box[0],box[1],prop['bins']), np.linspace(box[0],box[1],prop['bins']) ]         
            region = {'name':'BoxRegion','box':box}
            ids,coord = self.getPropertySimple(0,[region],ids)[0]
            weights = self.getPropertySimple(0,[prop['w']], ids=ids)[0]
            hist,xedges,yedges = np.histogram2d(coord[:,0], coord[:,1], bins=bins, weights=weights)
            return hist

        elif name=='AngularMomentum':
            # Example: {'name':'AngularMomentum','center':[0.5,0.5,0.5],'radius':0.5}
            region = {'name':'SphericalRegion','center':prop['center'],'radius':prop['radius']}
            ids, r2 = self.getPropertySimple(0,[region],ids)[0]
            pos, mass, vel = self.getPropertySimple(0,['Coordinates','Masses','Velocities'],ids=ids)
            m, (x,y,z), (vx,vy,vz) = mass, (pos-prop['center']).T, vel.T
            Lx,Ly,Lz = np.sum([ m*(y*vz-z*vy), m*(z*vx-x*vz), m*(x*vy-y*vx) ],axis=1) # total angular momentum
            return [Lx,Ly,Lz]

        elif name=='BoxProjection':
            # Example: {'name':'BoxProjection','transf':transf,'w':'Density','bins':200}
            transf = prop['transf']
            center = transf['preselect']['center']
            radius = transf['preselect']['radius']
            region = {'name':'SphericalRegion','center':center,'radius':radius}
            ids,r2 = self.getPropertySimple(0,[region],ids)[0]
            coord,mass = self.getPropertySimple(0,['Coordinates','Masses'],ids)
            
            # perform coordinate transformations
            coord = transf.convert(['translate','align','flip','rotate','postselect'],coord)
            mass = transf.select('postselect',mass)            

            # initiate a grid
            grid = apy.coord.grid( [prop['bins']]*3, transf['postselect']['box'] )
            pix = grid.getPixFromCoord(coord)
            grid.addAtPix('num',pix,1)
            grid.addAtPix('mass',pix,mass)

            # divide empty and full pixels
            pixFull = grid.data['num']>0
            pixEmpty = grid.data['num']==0            
            coordFull = grid.grid[pixFull]
            coordEmpty = grid.grid[pixEmpty]
            massFull = grid.data['mass'][pixFull]

            # for each empty pixel find the closest full pixel
            from scipy.spatial import cKDTree
            kdt = cKDTree(coordFull)
            dist,ngbEmpty = kdt.query(coordEmpty)
            numPix = np.full(pixFull.sum(),1,dtype=int)
            np.add.at(numPix,ngbEmpty,1)
            unitFullMass = massFull/numPix
            grid.data['mass'][pixFull] = unitFullMass
            grid.data['mass'][pixEmpty] = unitFullMass[ngbEmpty]

            # prepare projected properties
            properties = prop['w'] if isinstance(prop['w'],list) else [prop['w']]
            load = [pp for pp in properties if pp not in ['Masses','Density']]
            if len(load)>0:
                pps = self.getPropertySimple(0,load,ids)
                for p,pp in enumerate(pps):
                    pp = transf.select('postselect',pp)
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
                    box = transf['postselect']['box']
                    area = (box[1]-box[0])*(box[3]-box[2])
                    projection = mass / area * prop['bins']**2
                else:
                    ppk = 'pp%d'%i
                    projection = grid.data[ppk].sum(axis=2) / mass
                    i += 1
                data.append(projection)
            return data if isinstance(prop['w'],list) else data[0]
