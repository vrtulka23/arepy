from matplotlib import colors
import numpy as np

class norms:
    def __init__(self):
        self.norms = {}

    def setNorm(self,data,normID=None):
        
        #DEBUG: we have to do it like this, in case that the second dimensions are not the same
        data = np.array(data)
        if data.dtype==object:
            data = np.hstack([dat.ravel() for dat in data])
        vmin = np.nanmin(data)
        vmax = np.nanmax(data)
        vminpos = np.nanmin(data[data>0]) if np.sum(data>0)>0 else np.nanmax(data)

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

