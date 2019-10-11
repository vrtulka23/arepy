import numpy as np
import arepy as apy
import h5py as hp

class simpleMath:
    """Simple mathematical operation

    The properties in this class perform simple mathematical operations with the snapshot data
    """

    def prop_MathPlus(self,ids,ptype,**prop):
        """Addition of two datasets"""
        properties = apy.files.properties([prop['x'],prop['y']],ptype=ptype)
        data = self.getProperty(properties,ids,ptype=ptype)
        return data[properties[0]['key']] + data[properties[1]['key']]        

    def prop_MathMinus(self,ids,ptype,**prop):
        """Substraction of two datasets"""
        properties = apy.files.properties([prop['x'],prop['y']],ptype=ptype)
        data = self.getProperty(properties,ids,ptype=ptype)
        return data[properties[0]['key']] - data[properties[1]['key']]        

    def prop_MathMultiply(self,ids,ptype,**prop):
        """Multiplication of two datasets"""
        properties = apy.files.properties([prop['x'],prop['y']],ptype=ptype)
        data = self.getProperty(properties,ids,ptype=ptype)
        return data[properties[0]['key']] * data[properties[1]['key']]        

    def prop_MathDivide(self,ids,ptype,**prop):
        """Division of two datasets"""
        properties = apy.files.properties([prop['x'],prop['y']],ptype=ptype)
        data = self.getProperty(properties,ids,ptype=ptype)
        return data[properties[0]['key']] / data[properties[1]['key']]        

    def prop_MathModulo(self,ids,ptype,**prop):
        """Modulo of two datasets"""
        properties = apy.files.properties([prop['x'],prop['y']],ptype=ptype)
        data = self.getProperty(properties,ids,ptype=ptype)
        return data[properties[0]['key']] % data[properties[1]['key']]        
