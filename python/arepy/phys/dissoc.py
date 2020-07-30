import numpy as np
import arepy as apy

# Dissociation of the molecular hydrogen
#

class dissoc:

    def __enter__(self):
        return self
    def __exit__(self, type, value, tb):
        return
    def __init__(self,**opts):
        self.opt = {
            'Q':  1e50,        # ionization power of the source (phot/s)
            'nH': 1e10,        # number density of the hydrogen (cm^-3)
            'f':  1/(1+6.94),  # LW pumping factor
        }
        self.opt['nH2'] = self.opt['nH']/2 # number density of the molecular hydrogen (cm^-3)
        self.opt.update(opts)
        
    def getRadius(self,time):
        """Calculate radius
        
        We use this equation:
        n*4/3*pi*r^3 = f*Q*t
        """
        '''
        uvPumpFact = 6.94
        sigmaH = 5.23e-25
        sigmaH2 = 2.47e-18 * (1.0 + uvPumpFact)
        sigma = sigmaH + sigmaH2
        '''
        nPhot = self.opt['Q']*time*self.opt['f']
        '''
        nPhotH = nPhot * sigmaH / sigma
        nPhotH2 = nPhot * sigmaH2 / sigma
        nPhotdis = nPhotH2 / (1.0 + uvPumpFact);
        '''

        return ((nPhot)/(self.opt['nH2']*4/3*np.pi))**(1/3) # cm
        
