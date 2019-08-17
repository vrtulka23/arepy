import numpy as np

class collector():
    def __init__(self,*args):
        self.offset = {}
        self.data = {}
        self.length = {}
    def __len__(self,key=None):
        return len(self.data) if key is None else len(self.data[key])
    def __getitem__(self, key):
        return self.data[key]
    def __setitem__(self, key, value):
        self.data[key] = value
    def _set(self,ntot,ndata,key,value):
        shape = (ntot,)+value[:].shape[1:] if ntot>1 else value[:].shape
        self.data[key] = np.zeros(shape,dtype=value.dtype)
        self.offset[key] = 0
        self.length[key] = ntot
    def _add(self,ndata,key,value):
        if ndata==0: return
        m,n = self.offset[key], self.offset[key]+ndata
        self.data[key][m:n] = value[:]
        self.offset[key] += ndata

    # Add new stuff to collector
    # fid    - file index
    # ntot   - total number of data
    # ndata  - number of data in the current file
    # values - dictionary of the data
    def add(self,fid,ntot,ndata,values):
        for key,value in values.items():
            if fid==0:
                self._set(ntot,ndata,key,value)
            self._add(ndata,key,value)
    def trim(self):
        for key in self.data.keys():
            o = self.offset[key]
            if o<self.length[key]:
                self.length[key] = o
                self.data[key] = self.data[key][:o]
        return self
    def keys(self):
        return self.data.keys()
