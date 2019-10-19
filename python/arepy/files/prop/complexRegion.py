import numpy as np
import arepy as apy

class complexRegion:
    """Select particle values within a given region"""

    def _propRegion(self,ids,ptype,**prop):
        if 'p' in prop:
            # return properties in the selected region
            properties = apy.files.properties(prop['p'],ptype=ptype)
            del prop['p']
            region = self.getProperty(prop, ids=ids, ptype=ptype)
            return self.getProperty(properties, ids=region, ptype=ptype)
        else:
            # otherwise return only indexes
            return self.getProperty(prop, ids=ids, ptype=ptype) 

    def prop_RegionSphere(self,ids,ptype,**prop):
        """Select properties within a sphere region

        :param transf: Coordinate transformation
        :type transf: :class:`arepy.coord.transf`
        :param p: List of properties
        :type p: :class:`arepy.files.properties`
        :param [float]*3 center: Center of the sphere
        :param float radius: Radius of the sphere
        :return: Particle properties within the region

        .. note:
        
            If transformation is given, parameters 'center' and 'radius' will be ignored
        """
        prop['name'] = 'SelectSphere'
        if 'transf' in prop:
            prop['center'] = prop['transf']['select']['region'].center
            prop['radius'] = prop['transf']['select']['region'].radius
        return self._propRegion(ids,ptype,**prop)

    def prop_RegionBox(self,ids,ptype,**prop):
        """Select properties within a box region

        :param transf: Coordinate transformation
        :type transf: :class:`arepy.coord.transf`
        :param p: List of properties
        :type p: :class:`arepy.files.properties`
        :param [float]*6 center: Box limits
        :return: Particle properties within the region

        .. note:
        
            If transformation is given, parameter 'box' will be ignored
        """
        prop['name'] = 'SelectBox'
        if 'transf' in prop:
            prop['box'] = prop['transf']['select']['region'].limits
        return self._propRegion(ids,ptype,**prop)

    def prop_RegionIds(self,ids,ptype,**prop):           
        """Select properties of particles with IDs
        
        :param list[int] pids: One or more particle IDs
        :param p: List of properties
        :type p: :class:`arepy.files.properties`
        :return: Particle properties within the region
        """
        prop['name'] = 'SelectIds'
        return self._propRegion(ids,ptype,**prop)

    def prop_RegionFormationOrder(self,ids,ptype,**prop):
        """Select properties of sink particles with formation order IDs

        :param list[int] forder: One or more particle IDs
        :param p: List of properties
        :type p: :class:`arepy.files.properties`
        :return: Particle properties within the region
        """
        prop['name'] = 'SelectFormationOrder'
        return self._propRegion(ids,ptype,**prop)

    def prop_RegionPoints(self,ids,ptype,**prop):
        """Select property values at some coordinates

        :param list[[float]*3] coord: List of coordinates
        :param p: List of properties
        :type p: :class:`arepy.files.properties`
        :return: Properties of the closest particles to the points
        """
        prop['name'] = 'SelectPoints'
        return self._propRegion(ids,ptype,**prop)

    def prop_RegionCone(self,ids,ptype,**prop):
        """Select property values within a given cone region
        
        :param transf: Coordinate transformation
        :type transf: :class:`arepy.coord.transf`
        :param p: List of properties
        :type p: :class:`arepy.files.properties`
        :return: Particle properties within the region
        """
        # select a spherical region
        transf = prop['transf']
        region = self.getProperty({
            'name':'RegionSphere','transf':transf,
            'p':['Indexes','Coordinates']},
        ids=ids, ptype=ptype)

        # transform coordinates and indexes and cut out a cone
        region['Coordinates'] = transf.convert(['translate','align','flip','rotate','crop'],region['Coordinates'])
        idTrue = np.where(region['Indexes'])[0]   
        region['Indexes'][idTrue] = transf.items['crop']['ids'] 

        # get all data and return
        if 'p' in prop:
            properties = apy.files.properties(prop['p'])
            rprops = properties.getWithout('key',['Indexes','Coordinates'])
            rdata = self.getProperty(rprops,ids=region['Indexes'],ptype=ptype,dictionary=True)
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
