import numpy as np
import arepy as apy

class propSink:
    """Properties of the sink particle file"""

    def prop_SinkFormationOrder(self,prop,ids):
        """Returns value of the sink 'FormationOrder'"""
        return self.getSinkData('FormationOrder',ids)

    def prop_SinkFormationTime(self,prop,ids):
        """Returns value of the sink 'FormationTime'"""
        return self.getSinkData('FormationTime',ids)

    def prop_SinkID(self,prop,ids):
        """Returns value of the sink 'ID'"""
        return self.getSinkData('ID',ids)

    def prop_SinkMass(self,prop,ids):
        """Returns value of the sink 'Mass'"""
        return self.getSinkData('Mass',ids)

    def prop_SinkAccretionRate(self,prop,ids):
        """Returns value of the sink 'AccretionRate'"""
        return self.getSinkData('AccretionRate',ids)



    def prop_SelectFormationOrder(self,prop,ids):
        """Selecting particles from the list"""
        idsSelect = np.in1d(self.prop_SinkFormationOrder(prop,ids),prop['ids'])
        ids = np.where(ids, idsSelect, False)
        return self.getProperty(prop['p'],ids=ids,ptype=prop['ptype']) if 'p' in prop else ids
