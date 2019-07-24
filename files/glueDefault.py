import numpy as np
import arepy as apy

# Glues for the default properties
class glueDefault:

    ####################
    # Vector values
    ####################

    def glue_Coordinates(self,data):
        return np.vstack(data[prop['key']])
    def glue_Velocities(self,data):
        return np.vstack(data[prop['key']])

    ####################
    # Histograms
    ####################

    def glue_Histogram1D(self,data):
        return np.sum(data,axis=0) if self.opt['nsub']>1 else data
    def glue_Histogram2D(self,data):
        return np.sum(data,axis=0) if self.opt['nsub']>1 else data

    ####################
    # Statistics
    ####################

    def glue_Maximum(self,data):
        return np.array(data).flatten() if self.opt['nsub']>1 else data 
    def glue_Minimum(self,data):
        return np.array(data).flatten() if self.opt['nsub']>1 else data 
    def glue_Mean(self,data):
        return np.array(data).flatten() if self.opt['nsub']>1 else data 
    def glue_MinPos(self,data):
        return np.array(data).flatten() if self.opt['nsub']>1 else data 
    def glue_Sum(self,data):
        return np.array(data).flatten() if self.opt['nsub']>1 else data 

    ####################
    # Selections
    ####################

    def glue_RegionSphere(self,data):
            if self.opt['nsub']>1:
                rdata = [ [ s[0] for s in data ] ]
                for p in range(1,len(data[0])):
                    if np.ndim(data[0][p])>1:  # in case of coordinates, rates,...
                        d = np.vstack([ s[p] for s in data ])
                    else:                      # in case of masses, ids,...
                        d = np.hstack([ s[p] for s in data ])
                    rdata.append( d )
                data = rdata
