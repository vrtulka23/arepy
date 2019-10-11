import numpy as np
import arepy as apy
import h5py as hp

class simpleStat:
    """Simple statistics

    The properties in this class perform simple statistical operations on the snapshot data.
    """

    def prop_StatMinimum(self,ids,ptype,**prop):
        """Minimum value of a property"""
        properties = apy.files.properties(prop['p'],ptype=ptype)
        data = self.getProperty(properties,ids,ptype=ptype,dictionary=True)
        for pp in properties:
            properties.setData( pp['key'], np.min(data[pp['key']]) )
        return properties.getData()

    def prop_StatMinPos(self,ids,ptype,**prop):
        """Minimum positive value of a property"""
        properties = apy.files.properties(prop['p'],ptype=ptype)
        data = self.getProperty(properties,ids,ptype=ptype,dictionary=True)
        for pp in properties:
            ppdata = data[pp['key']]
            ppdata = [np.min(ppdata[ppdata>0])] if np.any(ppdata>0) else []
            properties.setData( pp['key'], np.min(values) )
        return properties.getData()

    def prop_StatMaximum(self,ids,ptype,**prop):
        """Maximum value of a property"""
        properties = apy.files.properties(prop['p'],ptype=ptype)
        data = self.getProperty(properties,ids,ptype=ptype,dictionary=True)
        for pp in properties:
            properties.setData( pp['key'], np.max(data[pp['key']]) )
        return properties.getData()
        
    def prop_StatMean(self,ids,ptype,**prop):
        """Mean value of a property"""
        properties = apy.files.properties(prop['p'],ptype=ptype)
        data = self.getProperty(properties,ids,ptype=ptype,dictionary=True)
        for pp in properties:
            properties.setData( pp['key'], np.mean(data[pp['key']]) )
        return properties.getData()

    def prop_StatSum(self,ids,ptype,**prop):
        """Sum of values of a property"""
        properties = apy.files.properties(prop['p'],ptype=ptype)
        data = self.getProperty(properties,ids,ptype=ptype,dictionary=True)
        for pp in properties:
            properties.setData( pp['key'], np.sum(data[pp['key']]) )
        return properties.getData()


    ###########################
    # Histograms
    ###########################

    def prop_Hist1D(self,ids,ptype,**prop):
        """Histogram of a single property"""
        properties = apy.files.properties(prop['x'],ptype=ptype)
        if 'w' in prop:
            properties.add(prop['w'])
        data = self.getProperty(properties,ids,ptype=ptype,dictionary=True)
        weights = data[properties[1]['key']] if 'w' in prop else None
        hist,edges = np.histogram(data[properties[0]['key']], 
                                  bins=prop['bins'], density=False, weights=weights)
        return hist

    def prop_Hist2D(self,ids,ptype,**prop):
        """Histogram of two properties"""
        properties = apy.files.properties([prop['x'],prop['y']],ptype=ptype)
        if 'w' in prop:
            properties.add(prop['w'])
        data = self.getProperty(properties,ids,ptype=ptype,dictionary=True)
        weights = data[properties[2]['key']] if 'w' in prop else None
        hist,xedges,yedges = np.histogram2d(data[properties[0]['key']], data[properties[1]['key']], 
                                            bins=prop['bins'], weights=weights) #, density=False)
        return hist
