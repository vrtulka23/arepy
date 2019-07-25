import arepy as apy
import numpy as np

class glueClass:

    def hasGlue(self,prop):
        return hasattr(self,'glue_'+prop['name'])

    def getGlue(self,prop,data):
        if self.hasGlue(prop):
            data[prop['key']] = getattr(self,'glue_'+prop['name'])(data[prop['key']])
        else:
            data[prop['key']] = np.hstack(data[prop['key']])
