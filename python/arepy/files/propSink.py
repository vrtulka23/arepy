import numpy as np
import arepy as apy

##################################
#
# A new property called NEW can be include simply by adding a new class method.
# For example:
#
# def prop_SinkNEW(self,prop,ids):
#     return self.getDataset('NEW',prop['ptype'],ids)
#
##################################

class propSink:

    ####################
    # Direct properties
    ####################

    def prop_SinkFormationOrder(self,prop,ids):
        return self.getSinkData('FormationOrder',ids)

    def prop_SinkFormationTime(self,prop,ids):
        return self.getSinkData('FormationTime',ids)

    def prop_SinkID(self,prop,ids):
        return self.getSinkData('ID',ids)

    def prop_SinkMass(self,prop,ids):
        return self.getSinkData('Mass',ids)

    def prop_SinkAccretionRate(self,prop,ids):
        return self.getSinkData('AccretionRate',ids)


    ##############################
    # Particle selections
    ##############################

    def prop_SelectFormationOrder(self,prop,ids):
        idsSelect = np.in1d(self.prop_SinkFormationOrder(prop,ids),prop['ids'])
        ids = np.where(ids, idsSelect, False)
        return self.getProperty(prop['p'],ids=ids,ptype=prop['ptype']) if 'p' in prop else ids
