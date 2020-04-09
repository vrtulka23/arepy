from matplotlib import colors
import numpy as np
import arepy as apy

class norms:
    def __init__(self):
        self.norms = {}

    def setNorm(self,data,normID=None):
        
        #DEBUG: we have to do it like this, in case that the second dimensions are not the same
        data = np.array(data)
        if data.dtype==object:
            data = np.hstack([np.ravel(dat) for dat in data])
        if None in data: # change None to NaN
            data = [np.nan if v is None else v for v in data]
        data = data[~np.isnan(data)]      # remove NaN
        if np.all(data==0): # do not norm zero arrays
            apy.shell.printc("Warning: excluding '%s' because it has only zero values (norms.py)"%normID,'r')
            return normID
        vmin = np.min(data)
        vmax = np.max(data)
        vminpos = np.min(data[data>0]) if np.sum(data>0)>0 else np.max(data)
        normID = 'NORMXYZ123_%d'%len(self.norms) if normID==None else str(normID)

        if normID in self.norms:
            oldNorm = self.norms[normID]
            if oldNorm['vmin']<vmin:
                vmin = oldNorm['vmin']
            if oldNorm['vminpos']<vminpos:
                vminpos = oldNorm['vminpos']
            if oldNorm['vmax']>vmax:
                vmax = oldNorm['vmax']

        self.norms[normID] = {'vmin':vmin,'vminpos':vminpos,'vmax':vmax}    
        return normID

    def getNorm(self,normID,normType='lin'):
        if normID not in self.norms:
            return None
        norm = self.norms[normID]
        if normType=='lin':
            return colors.Normalize(vmin=norm['vmin'],vmax=norm['vmax'])
        elif normType=='log':
            return colors.LogNorm(vmin=norm['vminpos'],vmax=norm['vmax'])
        else:
            return None

    def getLimits(self,normID):
        if normID not in self.norms:
            return None
        norm = self.norms[normID]
        return norm['vmin'], norm['vminpos'], norm['vmax']

