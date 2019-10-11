import numpy as np
import arepy as apy

# Import property classes
import arepy.files.prop as pc

# This part calculates complex properties from simple properties
class complex(pc.complexRegion,pc.complexSlice,pc.complexProj):
    """Complex properties"""

    def prop_MassCenter(self,ids,ptype,**prop):
        """Get mass center of a gas
        
        :param transf: Coordinate transformation
        :type transf: arepy.coord.transf
        :return: Mass center of the gas
        :rtype: [float]*3
        """
        if ptype is not None:
            pts = [ptype] if np.isscalar(ptype) else ptype
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
                },ids=ids,ptype=ptype)
            else: 
                rids = ids
            rdata = self.getProperty([
                {'name':'Masses','ptype':pt},
                {'name':'Coordinates','ptype':pt}
            ],ids=rids,ptype=ptype)
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

    # Example: {'name':'AngularMomentum','center':[0.5,0.5,0.5],'radius':0.5}
    def prop_AngularMomentum(self,ids,ptype,**prop):
        """Get angular momentum around some point
        
        :param [float]*3 center: Center of a sphere
        :param float radius: Radius of a sphere
        :return: Angular momentum vector
        :rtype: [float]*3
        """
        region = self.getProperty({
            'name':'RegionSphere','center':prop['center'],'radius':prop['radius'],
            'p': ['Coordinates','Masses','Velocities']
        },ids=ids,ptype=ptype)
        m, (x,y,z), (vx,vy,vz) = region['Masses'], (region['Coordinates']-prop['center']).T, region['Velocities'].T
        Lx,Ly,Lz = np.sum([ m*(y*vz-z*vy), m*(z*vx-x*vz), m*(x*vy-y*vx) ],axis=1) # total angular momentum
        return [Lx,Ly,Lz]

    #######################
    # Histograms
    #######################

    def prop_HistSphere(self,ids,ptype,**prop):
        """Mass weighted radial histogram of a property within a spherical region

        :param [float]*3 center: Center of the sphere
        :param list[float] bins: Radial bins
        :param properties p: List of properties 
        :return: Mass weighted radial distribution of a property

        Example::
            
            >>> snap.getProperty({
            >>>     'name':'HistSphere','center':[0.5,0.5,0.5],'bins':np.linspace(0,0.5,50),
            >>>     'p':['X_HP','Temperature']
            >>> })
            
            {'X_HP': [0.234, 0.64, 0.3,...],
             'Temperature': [1234.3, 3435.23, 9454.23,...]}
        """
        region = self.getProperty({
            'name':'RegionSphere','center':prop['center'],'radius':prop['bins'][-1],'ptype':ptype,
            'p':['Indexes',{'name':'Masses','ptype':ptype},{'name':'Radius2','center':prop['center']}]
        },ids=ids,ptype=ptype)
        wHist, edges = np.histogram(region['Radius2'],bins=prop['bins']**2,weights=region['Masses'],density=False)

        properties = apy.files.properties(prop['p'])
        data = self.getProperty(properties,ids=region['Indexes'],ptype=ptype,dictionary=True)
        for pp in properties:
            pHist, edges = np.histogram(region['Radius2'],bins=prop['bins']**2,
                                        weights=region['Masses']*data[pp['key']],density=False)
            properties.setData(pp['key'], pHist/wHist)
        return properties.getData()
        
    # Example: {'name':'HistBox','center':[0.5,0.5,0.5],'size':1,'w':'Masses','bins':200}
    def prop_HistBox(self,ids,ptype,**prop):
        """Two dimensional histogram of a property within a selected box region"""
        box = apy.coord.box(prop['size'],prop['center'])
        bins = [ np.linspace(box[0],box[1],prop['bins']), np.linspace(box[0],box[1],prop['bins']) ]         
        properties = apy.files.properties(['Coordinates',prop['w']])
        data = self.getProperty({'name':'RegionBox','box':box,'p':properties},ids=ids,ptype=ptype)
        hist,xedges,yedges = np.histogram2d(data['Coordinates'][:,0], data['Coordinates'][:,1], 
                                            bins=bins, weights=data[properties[1]['key']])
        return hist

    def prop_FractionVolume(self,ids,ptype,**prop):
        """Get a volume fraction of a property in some region
        
        :param properties p: List of properties
        :param float lt: Select cells with properties larger than this value
        :param float st: Select cells with properties smaller than this value
        :return: Volume fraction within the selected region
        :rtype: float or list[float]
        """
        volume = self.getProperty('CellVolume',ids=ids,ptype=ptype)
        volTot = np.sum(volume)
        properties = apy.files.properties(prop['p'])
        data = self.getProperty(properties,ids=ids,ptype=ptype)
        ids = np.ones((len(volume)), dtype=bool) #[True]*len(volume)
        if 'lt' in prop: # larger than
            ids = (ids & (data>prop['lt']))
        if 'st' in prop: # smaller than
            ids = (ids & (data<prop['st']))
        return np.sum(volume[ids])/volTot            

    def prop_FractionMass(self,ids,ptype,**prop):
        """Get mass fraction of some element
        
        :param prop p: A property or list of properties
        :return: Mass fraction within the selected region
        :rtype: float or list[float]
        """
        masses = self.getProperty('Masses',ids=ids,ptype=ptype)
        massTot = np.sum(masses)
        properties = apy.files.properties(prop['p'])
        data = self.getProperty(properties,ids=ids,ptype=ptype,dictionary=True)
        for pp in properties:
            key = pp['key']
            values = np.sum(data[key])/massTot
            properties.setData(key,values)
        return properties.getData()
