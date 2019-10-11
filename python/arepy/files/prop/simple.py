import numpy as np
import arepy as apy
import h5py as hp

class simple(apy.files.prop.simpleSelect,
             apy.files.prop.simpleMath,
             apy.files.prop.simpleStat):
    """Simple properties

    Properties in this class can be extracted directly from the Arepo snapshot.
    """

    def prop_ParticleIDs(self,ids,ptype,**prop):
        """Get cell IDs

        :return: Array with particle IDs
        :rtype: list[int]
        """
        return self.getSnapData('ParticleIDs',ptype,ids)

    def prop_Masses(self,ids,ptype,**prop):
        """Get cell masses

        :return: Array of particle masses
        :rtype: list[float]
        """
        return self.getSnapData('Masses',ptype,ids)

    def prop_Density(self,ids,ptype,**prop):
        """Get cell densities

        :return: Array of particle densities
        :rtype: list[float]
        """
        return self.getSnapData('Density',ptype,ids)

    def prop_InternalEnergy(self,ids,ptype,**prop):
        """Get cell internal energies

        :return: Array of particle internal energies
        :rtype: list[float]
        """
        return self.getSnapData('InternalEnergy',ptype,ids)

    def prop_Coordinates(self,ids,ptype,**prop):
        """Get cell coordinates

        :return: Array of particle coordinates
        :rtype: list[[float]*3]
        """
        return self.getSnapData('Coordinates',ptype,ids)

    def prop_PosX(self,ids,ptype,**prop):
        """Get cell x coordinates

        :return: Array of particle x coordinates
        :rtype: list[float]
        """
        return self.getSnapData('Coordinates',ptype,ids,0)

    def prop_PosY(self,ids,ptype,**prop):
        """Get cell y coordinates

        :return: Array of particle y coordinates
        :rtype: list[float]
        """
        return self.getSnapData('Coordinates',ptype,ids,1)

    def prop_PosZ(self,ids,ptype,**prop):
        """Get cell z coordinates

        :return: Array of particle z coordinates
        :rtype: list[float]
        """
        return self.getSnapData('Coordinates',ptype,ids,2)

    # velocity vector components
    def prop_Velocities(self,ids,ptype,**prop):
        """Get cell velocities

        :return: Array of particle velocities
        :rtype: list[[float]*3]
        """
        return self.getSnapData('Velocities',ptype,ids)

    def prop_VelX(self,ids,ptype,**prop):
        """Get cell x velocities

        :return: Array of particle x velocities
        :rtype: list[float]
        """
        return self.getSnapData('Velocities',ptype,ids,0)

    def prop_VelY(self,ids,ptype,**prop):
        """Get cell y velocities

        :return: Array of particle y velocities
        :rtype: list[float]
        """
        return self.getSnapData('Velocities',ptype,ids,1)

    def prop_VelZ(self,ids,ptype,**prop):
        """Get cell z velocities

        :return: Array of particle z velocities
        :rtype: list[float]
        """
        return self.getSnapData('Velocities',ptype,ids,2)

    def prop_FileIndex(self,ids,ptype,**prop):                 
        """Index of a file where the particle is saved"""
        npart = self.sf['Header'].attrs['NumPart_ThisFile'][ptype]
        return np.full(npart,self.fnum)

    # particle index within the file
    def prop_ParticleIndex(self,ids,ptype,**prop):       
        """Index of a particle within the dataset"""
        data = np.arange(self.sf['Header'].attrs['NumPart_ThisFile'][ptype])
        return data[ids]            
    
    ##########################
    # Derived properties
    ##########################

    # radius from a given center
    def prop_Radius(self,ids,ptype,**prop):                    
        """Get radius distances from a given center point

        :param [int,int,int] center: Center point coordinates
        :return: Cell distances from the center
        :rtype: list[int]
        """
        coord = self.prop_Coordinates(ids,ptype,**prop) - prop['center']
        return np.linalg.norm(coord,axis=1)

    # quadrate of the radius from a given center
    def prop_Radius2(self,ids,ptype,**prop):                   
        """Square of a particle radius from a given center"""
        coord = self.prop_Coordinates(ids,ptype,**prop) - prop['center']
        return coord[:,0]**2 + coord[:,1]**2 + coord[:,2]**2
        
    # size of the velocity tangent component
    def prop_VelocityRadial(self,ids,ptype,**prop):            
        """Radial component of the velocities

        :param [float]*3 center: Point from which the velocity component is calculated
        :return [float]*3: Radial velocity vector
        
        Calculation of the component is taken from Wikipedia_.

        .. _Wikipedia: https://en.wikipedia.org/wiki/Tangential_and_normal_components

        
        """
        rad = self.prop_Coordinates(ids,ptype,**prop) - prop['center']          # translated origin
        norm = np.linalg.norm(rad,axis=1)[:,None]
        nhat = np.where(norm>0,rad/norm,np.zeros_like(rad)) # unit radial vector
        return np.multiply(self.prop_Velocities(ids,ptype,**prop),nhat).sum(1)  # element-wise dot product (v.n_hat)

    # voronoi cell volume
    def prop_CellVolume(self,ids,ptype,**prop): 
        """Particle cell Volume

        :return float: Cell volume
        
        Volume of the cell is calculated from its mass and density:

        .. math::
            
            V = \\frac{M}{\\rho}
        """
        return self.prop_Masses(ids,ptype,**prop) / self.prop_Density(ids,ptype,**prop)
        
    # cell radius when assumed a spherical shape
    def prop_CellRadius(self,ids,ptype,**prop): 
        """Particle cell mean radius
        
        :return float: Mean cell radius

        Cell radius is only approximated from the cell volume:

        .. math::

            r = \\left( \\frac{3V}{4\\pi} \\right)^{1/3}
        """
        volume = self.prop_CellVolume(ids,ptype,**prop)
        return ((volume*3)/(4*np.pi))**(1./3.)
