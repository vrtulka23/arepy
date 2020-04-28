import numpy as np
import arepy as apy
import h5py as hp

class sgchem1:
    """SGChem properties

    Chemistry specific properties that can be used only with the primordial chemistry module SGChem.
    """

    ###############################
    # Chemical abundances
    ###############################

    def prop_ChemicalAbundances(self,ids,ptype,**prop):
        """Chemical abundances
        
        :return: List of chemical abundances
        :rtype: list[float]*9
        """
        return self.getSnapData('ChemicalAbundances',ptype,ids)
    def prop_x_H2(self,ids,ptype,**prop):
        """Abundance of a molecular Hydrogen
        
        :return: List of H2 abundances
        :rtype:  list[float]
        """
        return self.getSnapData('ChemicalAbundances',ptype,ids,0)
    def prop_x_HP(self,ids,ptype,**prop):
        """Abundance of a ionized Hydrogen
        
        :return: List of H+ abundances
        :rtype:  list[float]
        """
        return self.getSnapData('ChemicalAbundances',ptype,ids,1)
    def prop_x_DP(self,ids,ptype,**prop):
        """Abundance of a ionized Deuterium
        
        :return: List of D+ abundances
        :rtype:  list[float]
        """
        return self.getSnapData('ChemicalAbundances',ptype,ids,2)
    def prop_x_HD(self,ids,ptype,**prop):
        return self.getSnapData('ChemicalAbundances',ptype,ids,3)
    def prop_x_HEP(self,ids,ptype,**prop):
        return self.getSnapData('ChemicalAbundances',ptype,ids,4)
    def prop_x_HEPP(self,ids,ptype,**prop):
        return self.getSnapData('ChemicalAbundances',ptype,ids,5)
    def prop_x_H(self,ids,ptype,**prop):
        return self.opt['chem']['x0_H']  - 2*self.prop_x_H2(ids,ptype,**prop) - self.prop_x_HP(ids,ptype,**prop) - self.prop_x_HD(ids,ptype,**prop)
    def prop_x_HE(self,ids,ptype,**prop):
        return self.opt['chem']['x0_He'] - self.prop_x_HEP(ids,ptype,**prop)  - self.prop_x_HEPP(ids,ptype,**prop)
    def prop_x_D(self,ids,ptype,**prop):
        return self.opt['chem']['x0_D']  - self.prop_x_DP(ids,ptype,**prop)   - self.prop_x_HD(ids,ptype,**prop)

    ###############################
    # Mass fractions of species in the cell
    ###############################

    def prop_X_H2(self,ids,ptype,**prop):
        return self.opt['chem']['X_H'] * self.prop_x_H2(ids,ptype,**prop) * 2
    def prop_X_HP(self,ids,ptype,**prop):
        return self.opt['chem']['X_H'] * self.prop_x_HP(ids,ptype,**prop) * 1
    def prop_X_DP(self,ids,ptype,**prop):
        return self.opt['chem']['X_H'] * self.prop_x_DP(ids,ptype,**prop) * 2
    def prop_X_HD(self,ids,ptype,**prop):
        return self.opt['chem']['X_H'] * self.prop_x_HD(ids,ptype,**prop) * 3
    def prop_X_HEP(self,ids,ptype,**prop):
        return self.opt['chem']['X_H'] * self.prop_x_HEP(ids,ptype,**prop) * 4
    def prop_X_HEPP(self,ids,ptype,**prop):
        return self.opt['chem']['X_H'] * self.prop_x_HEPP(ids,ptype,**prop) * 4
    def prop_X_H(self,ids,ptype,**prop):
        return self.opt['chem']['X_H'] * self.prop_x_H(ids,ptype,**prop) * 1
    def prop_X_HE(self,ids,ptype,**prop):
        return self.opt['chem']['X_H'] * self.prop_x_HE(ids,ptype,**prop) * 4
    def prop_X_D(self,ids,ptype,**prop):
        return self.opt['chem']['X_H'] * self.prop_x_D(ids,ptype,**prop) * 2
        
    ###############################
    # Total mass of species in the cell (code units)
    ###############################

    def prop_M_H2(self,ids,ptype,**prop):
        return self.prop_X_H2(ids,ptype,**prop) *   self.prop_Masses(ids,ptype,**prop)
    def prop_M_HP(self,ids,ptype,**prop):
        return self.prop_X_HP(ids,ptype,**prop) *   self.prop_Masses(ids,ptype,**prop)
    def prop_M_DP(self,ids,ptype,**prop):
        return self.prop_X_DP(ids,ptype,**prop) *   self.prop_Masses(ids,ptype,**prop)
    def prop_M_HD(self,ids,ptype,**prop):
        return self.prop_X_HD(ids,ptype,**prop) *   self.prop_Masses(ids,ptype,**prop)
    def prop_M_HEP(self,ids,ptype,**prop):
        return self.prop_X_HEP(ids,ptype,**prop) *  self.prop_Masses(ids,ptype,**prop)
    def prop_M_HEPP(self,ids,ptype,**prop):
        return self.prop_X_HEPP(ids,ptype,**prop) * self.prop_Masses(ids,ptype,**prop)
    def prop_M_H(self,ids,ptype,**prop):
        return self.prop_X_H(ids,ptype,**prop) *    self.prop_Masses(ids,ptype,**prop)
    def prop_M_HE(self,ids,ptype,**prop):
        return self.prop_X_HE(ids,ptype,**prop) *   self.prop_Masses(ids,ptype,**prop)
    def prop_M_D(self,ids,ptype,**prop):
        return self.prop_X_D(ids,ptype,**prop) *    self.prop_Masses(ids,ptype,**prop)

    ###############################
    # Total number of species
    ###############################

    def prop_N_H2(self,ids,ptype,**prop):
        return self.opt['chem']['X_H'] * self.prop_x_H2(ids,ptype,**prop) *   self.prop_Masses(ids,ptype,**prop) / apy.const.m_p
    def prop_N_HP(self,ids,ptype,**prop):
        return self.opt['chem']['X_H'] * self.prop_x_HP(ids,ptype,**prop) *   self.prop_Masses(ids,ptype,**prop) / apy.const.m_p
    def prop_N_DP(self,ids,ptype,**prop):
        return self.opt['chem']['X_H'] * self.prop_x_DP(ids,ptype,**prop) *   self.prop_Masses(ids,ptype,**prop) / apy.const.m_p
    def prop_N_HD(self,ids,ptype,**prop):
        return self.opt['chem']['X_H'] * self.prop_x_HD(ids,ptype,**prop) *   self.prop_Masses(ids,ptype,**prop) / apy.const.m_p
    def prop_N_HEP(self,ids,ptype,**prop):
        return self.opt['chem']['X_H'] * self.prop_x_HEP(ids,ptype,**prop) *  self.prop_Masses(ids,ptype,**prop) / apy.const.m_p
    def prop_N_HEPP(self,ids,ptype,**prop):
        return self.opt['chem']['X_H'] * self.prop_x_HEPP(ids,ptype,**prop) * self.prop_Masses(ids,ptype,**prop) / apy.const.m_p
    def prop_N_H(self,ids,ptype,**prop):
        return self.opt['chem']['X_H'] * self.prop_x_H(ids,ptype,**prop) *    self.prop_Masses(ids,ptype,**prop) / apy.const.m_p
    def prop_N_HE(self,ids,ptype,**prop):
        return self.opt['chem']['X_H'] * self.prop_x_HE(ids,ptype,**prop) *   self.prop_Masses(ids,ptype,**prop) / apy.const.m_p
    def prop_N_D(self,ids,ptype,**prop):
        return self.opt['chem']['X_H'] * self.prop_x_D(ids,ptype,**prop) *    self.prop_Masses(ids,ptype,**prop) / apy.const.m_p

    ###############################
    # Photon ionization/heating rates 
    ###############################
 
    def prop_PhotonRates(self,ids,ptype,**prop):         
        return self.getSnapData('PhotonRates',ptype,ids)
    def prop_RIH(self,ids,ptype,**prop):         
        return self.getSnapData('PhotonRates',ptype,ids,0)
    def prop_HRIH(self,ids,ptype,**prop):         
        return self.getSnapData('PhotonRates',ptype,ids,1)
    def prop_RIH2(self,ids,ptype,**prop):         
        return self.getSnapData('PhotonRates',ptype,ids,2)
    def prop_HRIH2(self,ids,ptype,**prop):         
        return self.getSnapData('PhotonRates',ptype,ids,3)
    def prop_RDH2(self,ids,ptype,**prop):         
        return self.getSnapData('PhotonRates',ptype,ids,4)
    def prop_HRD(self,ids,ptype,**prop):         
        return self.getSnapData('PhotonRates',ptype,ids,5)
    def prop_RIHE(self,ids,ptype,**prop):         
        return self.getSnapData('PhotonRates',ptype,ids,6)
    def prop_HRIHE(self,ids,ptype,**prop):         
        return self.getSnapData('PhotonRates',ptype,ids,7)


    ###############################
    # Photon fluxes in the cell (photons per second)
    ###############################

    def prop_PhotonFlux(self,ids,ptype,**prop):         
        return self.getSnapData('PhotonFlux',ptype,ids) * self.units['flux']
    def prop_F056(self,ids,ptype,**prop):
        return self.getSnapData('PhotonFlux',ptype,ids,0) * self.units['flux']
    def prop_F112(self,ids,ptype,**prop):
        return self.getSnapData('PhotonFlux',ptype,ids,1) * self.units['flux']
    def prop_F136(self,ids,ptype,**prop):
        return self.getSnapData('PhotonFlux',ptype,ids,2) * self.units['flux']
    def prop_F152(self,ids,ptype,**prop):
        return self.getSnapData('PhotonFlux',ptype,ids,3) * self.units['flux']
    def prop_F246(self,ids,ptype,**prop):
        return self.getSnapData('PhotonFlux',ptype,ids,4) * self.units['flux']
    def prop_FTOT(self,ids,ptype,**prop):
        return np.sum(self.prop_PhotonFlux(ids,ptype,**prop),axis=1)


    ###############################
    # Derived properties
    ###############################

    # Polytropic index
    def prop_Gamma(self,ids,ptype,**prop):
        """Polytropic index
        
        :return: If value of Gamma is not present in a snapshot this returns a standard value of Gamma=5/3
        """
        if self.hasSnapData('Gamma',ptype):
            return self.getSnapData('Gamma',ptype,ids)
        else:
            return apy.const.gamma    
    
    # Temperature of the gas (K)
    def prop_Temperature(self,ids,ptype,**prop):
        # The follwoing seems to be wrong
        #inten = self.sf[pt]['InternalEnergy'][:]
        #utherm = inten[ids] * self.sf['Header'].attrs['UnitVelocity_in_cm_per_s']**2
        #return ( calcGamma() - 1. ) * utherm * (calcMu() * apy.const.m_p) / apy.const.k_B
    
        # The following calculation was taken from voronoi_makeimage.c line 2240 
        # and gives the same temperatures as are shown on the Arepo images
        dens = self.prop_Density(ids,ptype,**prop)
        yn = dens * self.units['density'] / ((1.0 + 4.0 * self.opt['chem']['x0_He']) * apy.const.m_p)
        en = self.prop_InternalEnergy(ids,ptype,**prop) * dens * self.units['energy'] / self.units['volume']
        yntot = (1.0 + self.opt['chem']['x0_He'] - self.prop_x_H2(ids,ptype,**prop) + self.prop_x_HP(ids,ptype,**prop) + \
                 self.prop_x_HEP(ids,ptype,**prop) + self.prop_x_HEPP(ids,ptype,**prop) ) * yn
        return (self.prop_Gamma(ids,ptype,**prop) - 1.0) * en / (yntot * apy.const.k_B) 

    # Mean molecular weight
    def prop_Mu(self,ids,ptype,**prop):
        xHP = self.prop_x_HP(ids,ptype,**prop)
        xDP = self.prop_x_DP(ids,ptype,**prop)
        xHEP = self.prop_x_HEP(ids,ptype,**prop)
        xHEPP = self.prop_x_HEPP(ids,ptype,**prop)
        mu = ( self.opt['chem']['x0_H'] + 2.*self.opt['chem']['x0_D'] + 4.*self.opt['chem']['x0_He'] ) / \
             ( self.opt['chem']['x0_H'] + self.opt['chem']['x0_D'] + self.opt['chem']['x0_He'] + \
               xHP + xDP + xHEP + 2*xHEPP )
        return mu
    
    # Number density of the gas (cm^{-3})
    def prop_NumberDensity(self,ids,ptype,**prop):
        density = self.prop_Density(ids,ptype,**prop) * self.units['density']  # density (g/cm^3)
        mu = self.prop_Mu(ids,ptype,**prop)
        return density / ( apy.const.m_p * mu )        

    # Pressure (code units of g/cm^3*cm^2/s^2 = g/cm/s^2 = dyne/cm^2 = barye)
    def prop_Pressure(self,ids,ptype,**prop):
        dens = self.prop_Density(ids,ptype,**prop)
        gamma = self.prop_Gamma(ids,ptype,**prop)
        u = self.prop_InternalEnergy(ids,ptype,**prop)
        return (gamma-1.) * dens * u

    # Recombination factor of Hydrogen and Helium type B from sx_chem_sgchem.c and SGChem/coolinmo.F (rec*cm^3/s)
    def prop_AlphaB(self,ids,ptype,**prop):
        tinv = 1.0 / self.prop_Temperature(ids,ptype,**prop)
        return 2.753e-14 * (315614 * tinv)**1.5 / ( 1. + (115188 * tinv)**0.407 )**2.242
    def prop_AlphaBHe(self,ids,ptype,**prop):
        temp = self.prop_Temperature(ids,ptype,**prop)
        logT = np.log10( temp )
        return 1e-11 * (11.19e0 - 1.676e0 * logT - 0.2852e0 * logT * logT 
                        + 4.433e-2 * logT * logT * logT) / np.sqrt(temp);

    # Recombination rate of Hydrogen and Helium (rec/s)
    def prop_RecombH(self,ids,ptype,**prop): 
        density = self.prop_Density(ids,ptype,**prop) * self.units['density']  # density (g/cm^3)
        numdens = density / ((1. + 4. * self.opt['chem']['x0_He']) * apy.const.m_p); # nucleon number density [1/cm^3]
        return self.prop_AlphaB(ids,ptype,**prop) * numdens
    def prop_RecombHe(self,ids,ptype,**prop): 
        density = self.prop_Density(ids,ptype,**prop) * self.units['density']  # density (g/cm^3)
        numdens = density / ((1. + 4. * self.opt['chem']['x0_He']) * apy.const.m_p); # nucleon number density [1/cm^3]
        return self.prop_AlphaBHe(ids,ptype,**prop) * numdens

    # Stromgren radius if a source is in the cell (physical code units)
    def prop_StromgrenRadius(self,ids,ptype,**prop):
        alpha = prop['alpha'] if 'alpha' in prop else self.prop_AlphaB(ids,ptype,**prop)         # (rec*cm^3/s)
        ndens = prop['ndens'] if 'ndens' in prop else self.prop_NumberDensity(ids,ptype,**prop)  # (cm^{-3})
        flux  = prop['flux']  if 'flux'  in prop else np.sum(self.prop_PhotonFlux(ids,ptype,**prop)[:,2:],axis=1) # (phot/s)
        temp  = prop['temp']  if 'temp'  in prop else self.prop_Temperature(ids,ptype,**prop)    # (K)
        gamma = prop['gamma'] if 'gamma' in prop else self.prop_Gamma(ids,ptype,**prop)        
        mu    = prop['mu']    if 'mu'    in prop else self.prop_Mu(ids,ptype,**prop)
        test = apy.phys.IonizationFrontTest(a=alpha, n=ndens, Q=flux, T_avg=temp, gamma=gamma, mu=mu)
        return test.r_st / self.units['length'] 

    # Sound speed (code units)
    # Formula taken from: https://en.wikipedia.org/wiki/Speed_of_sound
    # Chapter: Speed of sound in ideal gases and air
    def prop_SoundSpeed(self,ids,ptype,**prop):
        temp  = prop['temp']  if 'temp'  in prop else self.prop_Temperature(ids,ptype,**prop)  # (K)
        gamma = prop['gamma'] if 'gamma' in prop else self.prop_Gamma(ids,ptype,**prop)        
        mu    = prop['mu']    if 'mu'    in prop else self.prop_Mu(ids,ptype,**prop)
        return np.sqrt( (gamma * apy.const.k_B * temp) / (mu * apy.const.m_p) ) / self.units['velocity']

    def prop_ToomreQ(self,ids,ptype,**prop):
        density = self.prop_Density(ids,ptype,**prop) * self.units['density']     # density (g/cm^3)
        csound = self.prop_SoundSpeed(ids,ptype,**prop) * self.units['velocity']  # cm/s
        kappa = 1 # ??????
        toomre = ( csound * kappa ) / ( apy.const.G * np.pi * density )
        # DEBUG: nned to be implemented
