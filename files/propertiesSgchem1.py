import numpy as np
import arepy as apy
import h5py as hp

class propertiesSgchem1:
    #########################
    # Helper functions
    #########################
    
    def _calcGamma(self,prop,ids):
        if 'Gamma' in self.sf['PartType%d'%prop['ptype']]:
            gamma = self.sf['PartType%d/Gamma'%prop['ptype']][:]
            return gamma[ids]
        else:
            return apy.const.gamma
    
    def _calcTemp(self,prop,ids):   # returns temperature in K
        # The follwoing seems to be wrong
        #inten = self.sf[pt]['InternalEnergy'][:]
        #utherm = inten[ids] * self.sf['Header'].attrs['UnitVelocity_in_cm_per_s']**2
        #return ( calcGamma() - 1. ) * utherm * (calcMu() * apy.const.m_p) / apy.const.k_B
    
        # The following calculation was taken from voronoi_makeimage.c line 2240 
        # and gives the same temperatures as are shown on the Arepo images
        dens     = self.sf['PartType%d/Density'%prop['ptype']][:]
        energy   = self.sf['PartType%d/InternalEnergy'%prop['ptype']][:]
        x_h2, x_Hp, x_DP, x_HD, x_Hep, x_Hepp = self.sf['PartType%d/ChemicalAbundances'%prop['ptype']][:].T
        yn = dens[ids] * self.units['density'] / ((1.0 + 4.0 * self.chem['x0_He']) * apy.const.m_p)
        en = energy[ids] * dens[ids] * self.units['energy'] / self.units['volume']
        yntot = (1.0 + self.chem['x0_He'] - x_h2[ids] + x_Hp[ids] + x_Hep[ids] + x_Hepp[ids]) * yn
        temp_in_K = (self._calcGamma(prop,ids) - 1.0) * en / (yntot * apy.const.k_B)
        return temp_in_K

    def _unitDensity(self,prop,ids):
        if self.comoving:
            h = self.sf['Header'].attrs['HubbleParam']
            a = self.sf['Header'].attrs['Time']
            density2cgs = ( self.units['mass'] * h**2 ) / (a * self.units['length'] )**3
        else:
            density2cgs = self.units['mass'] / self.units['length']**3
        return density2cgs

    def _calcMu(self,prop,ids):
        x_h2, x_Hp, x_DP, x_HD, x_Hep, x_Hepp = self.sf['PartType%d/ChemicalAbundances'%prop['ptype']][:].T
        mu = ( self.chem['x0_H'] + 2.*self.chem['x0_D'] + 4.*self.chem['x0_He'] ) / \
            ( self.chem['x0_H'] + self.chem['x0_D'] + self.chem['x0_He'] + x_Hp[ids] + x_DP[ids] + \
              x_Hep[ids] + 2.*x_Hepp[ids] )
        return mu
    
    def _calcNumDens(self,prop,ids):    # returns particle number density in code [1/cm^3]
        dens = self.sf['PartType%d/Density'%prop['ptype']][:]
        return dens[ids] * self._unitDensity(prop,ids) / ( apy.const.m_p * self._calcMu(prop,ids) )        

    def _calcAlphaB(self,prop,ids):  # case B recombination rate coefficients from SGChem/coolinmo.F
        tinv = 1.0 / self._calcTemp(prop,ids);
        return 2.753e-14 * (315614 * tinv)**1.5 / ( 1. + (115188 * tinv)**0.407 )**2.242;  # [rec*cm^3/s]        

    ###############################
    # Direct properties
    ###############################
    

    
    ###############################
    # Derived properties
    ###############################
    
    # Temperature of the gas
    def property_Temperature(self,prop,ids):
        return self._calcTemp(prop,ids)

    # Polytropic index
    def property_Gamma(self,prop,ids):
        return self._calcGamma(prop,ids)

    # Mean molecular weight
    def property_Mu(self,prop,ids):
        return self._calcMu(prop,ids)

    # Recombination factor of Hydrogen type B
    def property_AlphaB(self,prop,ids):
        return self._calcAlphaB(prop,ids)

    # Number density of the gas
    def property_NumberDensity(self,prop,ids):
        return self._calcNumDens(prop,ids)

    def property_Pressure(self,prop,ids):
        rho = self.sf['PartType%d/Density'%prop['ptype']][:]
        u   = self.sf['PartType%d/InternalEnergy'%prop['ptype']][:]
        return (self._calcGamma(prop,ids)-1.)*rho[ids]*u[ids]  # [cu]

    def property_RecombH(self,prop,ids):
        dens = self.sf['PartType%d/Density'%prop['ptype']][:]
        density =  dens[ids] * self._unitDensity(prop,ids);                               # density [g/cm^3]
        numdens = density / ((1. + 4. * self.chem['x0_He']) * apy.const.m_p); # nucleon number density [1/cm^3]
        return self._calcAlphaB(prop,ids) * numdens    # [rec/s]

    def property_StromgrenRadius(self,prop,ids):                # Stromgren radius
        flux = self.sf['PartType%d/PhotonFlux'%prop['ptype']][:]
        test = apy.phys.IonizationFrontTest(
            a=self._calcAlphaB(prop,ids), n=self._calcNumDens(prop,ids),
            Q=np.sum(flux[ids,2:],axis=1) * uFlux,    # total flux from 13.6+ eV
            T_avg=self._calcTemp(prop,ids), gamma=self._calcGamma(prop,ids), mu=self._calcMu(prop,ids)
        )
        return test.r_st / uLength # [cu]

    def property_PhotonFlux(self,prop,ids):                     # Photon flux in bins
        flux = self.sf['PartType%d/PhotonFlux'%prop['ptype']][:]
        return flux[ids,:] * self.units['flux']

    def property_FTOT(self,prop,ids):                # Total photon flux
        flux = fileSnap['PartType%d/PhotonFlux'%prop['ptype']][:]
        return np.sum(flux[ids],axis=1) * self.units['flux']
