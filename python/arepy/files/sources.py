import numpy as np
import arepy as apy

class sources:
    """Source list class

    This class reads, modifies and saves files with SPRAI sources

    :param str fileName: Name of a source file
    
    :var int nSources: Number of sources
    :var int nFreq: Number of spectral power
    :var int nSigma: Number of reaction cross-sections
    :var int nEnergy: Number of photon excessive energies
    
    .. note:
        
        One has to always set sources and their spectral power.
        The cross-sections and energies are optional and if they are missing SPRAI will calculate them.
    """
    
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
        """Add sources to the list

        :param list[[float]*3] coord: A list of source coordinates
        :param list[[float]*nFreq] sed: A list of source spectral power (ph/s)
        """
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
        """Add cross-sections
        
        :param [float]*nSigma sigma: List of cross-sections
        """
        self.nSigma = len(sigma)
        self.sigma = np.array(sigma)

    def addEnergies(self,energy):
        """Add excessive energies
        
        :param [float]*nEnergy energy: List of excessive energies
        """
        self.nEnergy = len(energy)
        self.energy = np.array(energy)

    def read(self,fileName):
        """Read a source file

        :param str fileName: Path to a source file
        """
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
        """Save a new source file

        :param str fileName: Path to a new source file
        """
        with open(fileName, 'wb') as f:
            np.array([self.nSigma,self.nEnergy,self.nSources,self.nFreq]).astype('u4').tofile(f)
            if self.sigma is not None:
                self.sigma.astype('f8').tofile(f)
            if self.energy is not None:
                self.energy.astype('f8').tofile(f)
            np.ravel(self.coord).astype('f8').tofile(f)
            np.ravel(self.sed).astype('f8').tofile(f)

    def show(self,limit=None):
        """Print out source file values to the terminal

        :param int limit: Maximum number of sources to show
        """
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
