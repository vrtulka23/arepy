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

        elif name=='BoxProjection':
            # Example: {'name':'BoxProjection','transf':transf,'w':'Density','bins':200}
            transf = prop['transf']
            center = transf['preselect']['center']
            radius = transf['preselect']['radius']
            region = {'name':'SphericalRegion','center':center,'radius':radius}
            ids,r2 = self.getPropertySimple(0,[region],ids)[0]
            if prop['w'] in ['Masses','Density']: # results in (g) and (g/cm^2)
                coord,mass = self.getPropertySimple(0,['Coordinates','Masses'],ids)
            else: # arbitrary mass weighted projected property
                coord,mass,pp = self.getPropertySimple(0,['Coordinates','Masses',prop['w']],ids)

            # perform rest of the transformations
            coord = transf.convert('translate',coord)
            if 'rotate' in transf.items:
                coord = transf.convert('rotate',coord)
            coord = transf.convert('postselect',coord)
            
            # initiate a grid
            grid = apy.coord.grid( [prop['bins']]*3, transf['postselect']['box'] )
            pix = grid.getPixFromCoord(coord)
            grid.addAtPix('num',pix,1)
            grid.addAtPix('mass',pix,mass)
            if prop['w'] not in ['Masses','Density']:
                grid.addAtPix('pp',pix,pp*mass)

            # divide empty and full pixels
            pixFull = grid.data['num']>0
            pixEmpty = grid.data['num']==0            
            coordFull = grid.grid[pixFull]
            coordEmpty = grid.grid[pixEmpty]
            massFull = grid.data['mass'][pixFull]
            massEmpty = grid.data['mass'][pixEmpty]

            # for each empty pixel find the closest full pixel
            from scipy.spatial import cKDTree
            kdt = cKDTree(coordFull)
            dist,ngbEmpty = kdt.query(coordEmpty)
            numPix = np.full(pixFull.sum(),1,dtype=int)
            np.add.at(numPix,ngbEmpty,1)
            unitFullMass = massFull/numPix
            grid.data['mass'][pixFull] = unitFullMass
            grid.data['mass'][pixEmpty] = unitFullMass[ngbEmpty]
            if prop['w'] not in ['Masses','Density']:
                unitFullPP = grid.data['pp'][pixFull]/numPix
                grid.data['pp'][pixFull] = unitFullPP
                grid.data['pp'][pixEmpty] = unitFullPP[ngbEmpty]
            
            # do some final corrections
            if prop['w']=='Masses':
                projection = grid.data['mass'].sum(axis=2)
            elif prop['w']=='Density':
                box = transf['postselect']['box']
                area = (box[1]-box[0])*(box[3]-box[2])
                projection = grid.data['mass'].sum(axis=2) / area * prop['bins']**2
            else:
                projection = grid.data['pp'].sum(axis=2) / grid.data['mass'].sum(axis=2)
            return projection
