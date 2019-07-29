import numpy as np
import arepy as apy

class sources:

    def __enter__(self):
        return self
        
    def __exit__(self, type, value, tb):
        return

    def __init__(self,fileName=None):
        self.nSources = 0
        self.nFreq = 0
        self.nSigma = 0
        self.nEnergy = 0
        self.coord = []
        self.sed = []
        self.sigma = None
        self.energy = None
        
        if fileName!=None:
            self.read(fileName)
    
    def addSource(self,coord,sed):
        if np.ndim(coord)==1:
            coord,sed = [coord],[sed]
        if self.nSources==0:
            self.coord = np.array(coord)
            self.sed = np.array(sed)
            self.nFreq = self.sed.shape[1]
        else:
            self.coord = np.append(self.coord,coord,axis=0)
            self.sed = np.append(self.sed,sed,axis=0)
        self.nSources = self.sed.shape[0]

    def addCrossSections(self,sigma):
        self.nSigma = len(sigma)
        self.sigma = np.array(sigma)

    def addEnergies(self,energy):
        self.nEnergy = len(energy)
        self.energy = np.array(energy)

    def read(self,fileName):
        with open(fileName, 'r') as f:
            nSigma, nEnergy, nSources, nFreq  = np.fromfile(f,dtype='u4',count=4)
            self.nSources = nSources
            self.nFreq = nFreq
            self.nSigma = nSigma
            self.nEnergy = nEnergy
            self.sigma = np.fromfile(f,dtype='f8',count=nSigma) if nSigma>0 else None
            self.energy = np.fromfile(f,dtype='f8',count=nEnergy) if nEnergy>0 else None 
            self.coord = np.fromfile(f,dtype='f8',count=nSources*3).reshape((nSources,3))
            self.sed = np.fromfile(f,dtype='f8',count=nSources*nFreq).reshape((nSources,nFreq))

    def write(self,fileName):
        with open(fileName, 'wb') as f:
            np.array([self.nSigma,self.nEnergy,self.nSources,self.nFreq]).astype('u4').tofile(f)
            if self.sigma is not None:
                self.sigma.astype('f8').tofile(f)
            if self.energy is not None:
                self.energy.astype('f8').tofile(f)
            np.ravel(self.coord).astype('f8').tofile(f)
            np.ravel(self.sed).astype('f8').tofile(f)

    def show(self,limit=None):
        if self.sigma is not None:
            print( 'Cross sections:  ', self.sigma )
        if self.energy is not None:
            print( 'Excess energies: ', self.energy )
        ids = slice(limit) if limit else slice(self.nSources)
        tab = apy.data.table()
        tab.column('x',self.coord[ids,0])
        tab.column('y',self.coord[ids,1])
        tab.column('z',self.coord[ids,2])
        for f in range(self.nFreq):
            tab.column('sed %d'%f,self.sed[ids,f])
        tab.show()
