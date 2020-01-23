import arepy as apy 
import numpy as np

class {{namePlot}}(apy.scripy.plot):
    def settings(self):
        self.opt['simOpt'] = {
            'initUnitsNew': {'length':apy.const.au},
            'initImages':True,
            'initSinks':True,
            'initSnap': True,
        }
    
