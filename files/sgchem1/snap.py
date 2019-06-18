import numpy as np
import arepy as apy
from arepy.files.sgchem1 import constants as const

def getHeader(fileSnap,name):
    if name in ['UnitMass_in_g','UnitLength_in_cm','UnitVelocity_in_cm_per_s',\
                'Flag_DoublePrecision','ComovingIntegrationOn']:
        return fileSnap['Header'].attrs[name]
    elif name=='ExpansionFactor':
        return fileSnap['Header'].attrs['Time']
    elif name=='Redshift':
        return 1./fileSnap['Header'].attrs['Time']-1.
    elif name=='UnitPhotons_per_s':
        return fileSnap['Parameters'].attrs['UnitPhotons_per_s']
    
def getProperty(fileSnap,ptype,name,ids,comoving,optChem):
    pt = 'PartType%d'%ptype

    nameStd = ['Masses','Velocities','PhotonFluxTotal']

    uMass =    fileSnap['Header'].attrs['UnitMass_in_g']
    uLength =  fileSnap['Header'].attrs['UnitLength_in_cm']
    uVolume  = fileSnap['Header'].attrs['UnitLength_in_cm']**3
    uDensity = fileSnap['Header'].attrs['UnitMass_in_g']/uVolume
    uEnergy  = fileSnap['Header'].attrs['UnitVelocity_in_cm_per_s']**2 * fileSnap['Header'].attrs['UnitMass_in_g']
    if 'UnitPhotons_per_s' in fileSnap['Parameters'].attrs:
        uFlux =    fileSnap['Parameters'].attrs['UnitPhotons_per_s']

    def unitDensity():
        if comoving:
            h = fileSnap['Header'].attrs['HubbleParam']
            a = fileSnap['Header'].attrs['Time']
            density2cgs = ( uMass * h**2 ) / (a * uLength )**3
        else:
            density2cgs = uMass / uLength**3
        return density2cgs

    def calcMu():
        x_h2, x_Hp, x_DP, x_HD, x_Hep, x_Hepp = fileSnap[pt]['ChemicalAbundances'][:].T
        mu = ( optChem['x0_H'] + 2.*optChem['x0_D'] + 4.*optChem['x0_He'] ) / \
            ( optChem['x0_H'] + optChem['x0_D'] + optChem['x0_He'] + x_Hp[ids] + x_DP[ids] + \
              x_Hep[ids] + 2.*x_Hepp[ids] )
        return mu

    def calcGamma():
        if 'Gamma' in fileSnap[pt]:
            gamma = fileSnap[pt]['Gamma'][:]
            return gamma[ids]
        else:
            return apy.const.gamma

    def calcTemp():   # returns temperature in K
        # The follwoing seems to be wrong
        #inten = fileSnap[pt]['InternalEnergy'][:]
        #utherm = inten[ids] * fileSnap['Header'].attrs['UnitVelocity_in_cm_per_s']**2
        #return ( calcGamma() - 1. ) * utherm * (calcMu() * apy.const.m_p) / apy.const.k_B
    
        # The following calculation was taken from voronoi_makeimage.c line 2240 
        # and gives the same temperatures as are shown on the Arepo images
        dens     = fileSnap[pt]['Density'][:]
        energy   = fileSnap[pt]['InternalEnergy'][:]
        x_h2, x_Hp, x_DP, x_HD, x_Hep, x_Hepp = fileSnap[pt]['ChemicalAbundances'][:].T
        yn = dens[ids] * uDensity / ((1.0 + 4.0 * optChem['x0_He']) * apy.const.m_p)
        en = energy[ids] * dens[ids] * uEnergy / uVolume
        yntot = (1.0 + optChem['x0_He'] - x_h2[ids] + x_Hp[ids] + x_Hep[ids] + x_Hepp[ids]) * yn
        temp_in_K = (calcGamma() - 1.0) * en / (yntot * apy.const.k_B)
        return temp_in_K

    def calcAlphaB():  # case B recombination rate coefficients from SGChem/coolinmo.F
        tinv = 1.0 / calcTemp();
        return 2.753e-14 * (315614 * tinv)**1.5 / ( 1. + (115188 * tinv)**0.407 )**2.242;  # [rec*cm^3/s]        

    def abund(i,ids):
        if i<6:
            abund = fileSnap[pt]['ChemicalAbundances'][:,i]
            return abund[ids]
        elif i==6: # x_H
            x_H2 = fileSnap[pt]['ChemicalAbundances'][:,0]
            x_HP = fileSnap[pt]['ChemicalAbundances'][:,1]
            x_HD = fileSnap[pt]['ChemicalAbundances'][:,3]
            return optChem['x0_H'] - 2*x_H2[ids] - x_HP[ids]- x_HD[ids]
        elif i==7: # x_He
            x_HEP = fileSnap[pt]['ChemicalAbundances'][:,4]
            x_HEPP = fileSnap[pt]['ChemicalAbundances'][:,5]
            return optChem['x0_He'] - x_HEP[ids] - x_HEPP[ids]
        elif i==8: # x_D
            x_DP = fileSnap[pt]['ChemicalAbundances'][:,2]
            x_HD = fileSnap[pt]['ChemicalAbundances'][:,3]
            return optChem['x0_D'] - x_DP[ids] - x_HD[ids]

    def calcNumDens():    # returns particle number density in code [1/cm^3]
        dens = fileSnap[pt]['Density'][:]
        return dens[ids] * unitDensity() / ( apy.const.m_p * calcMu() )        

    if name=='Mu':                           # mean molecular weight
        return calcMu()

    elif name=='Temperature':
        return calcTemp()

    elif name=='Gamma':
        return calcGamma()

    elif name=='AlphaB':
        return calcAlphaB()
        
    elif name=='NumberDensity':
        return calcNumDens()

    elif name=='Pressure':
        rho = fileSnap[pt]['Density'][:]
        u   = fileSnap[pt]['InternalEnergy'][:]
        return (calcGamma()-1.)*rho[ids]*u[ids]  # [cu]

    elif name=='RecombH':
        dens = fileSnap[pt]['Density'][:]
        density =  dens[ids] * unitDensity();                               # density [g/cm^3]
        numdens = density / ((1. + 4. * optChem['x0_He']) * apy.const.m_p); # nucleon number density [1/cm^3]
        return calcAlphaB() * numdens    # [rec/s]

    elif name=='StromgrenRadius':                # Stromgren radius
        flux = fileSnap[pt]['PhotonFlux'][:]
        test = apy.phys.IonizationFrontTest(
            a=calcAlphaB(), n=calcNumDens(),
            Q=np.sum(flux[ids,2:],axis=1) * uFlux,    # total flux from 13.6+ eV
            T_avg=calcTemp(), gamma=calcGamma(), mu=calcMu()
        )
        return test.r_st / uLength # [cu]

    elif name=='PhotonFlux':                     # Photon flux in bins
        flux = fileSnap[pt]['PhotonFlux'][:]
        return flux[ids,:] * uFlux

    elif name=='PhotonFluxTotal':                # Total photon flux
        flux = fileSnap[pt]['PhotonFlux'][:]
        return np.sum(flux[ids],axis=1) * uFlux
        
    elif name in const.orderPhotonFlux:          # Photon Flux in a particular bin
        i = const.orderPhotonFlux.index(name)
        flux = fileSnap[pt]['PhotonFlux'][:]
        return flux[ids,i] * uFlux
        
    elif name in const.orderAbund:               # Abundances
        i = const.orderAbund.index(name)
        return abund(i,ids)

    elif name in const.orderMassFract:           # Mass fractions
        i = const.orderMassFract.index(name)
        return optChem['X_H'] * abund(i,ids) * const.orderAtomicWeight[i]

    elif name in const.orderMassTotal:           # Total masses
        masses = fileSnap[pt]['Masses'][:]
        i = const.orderMassTotal.index(name)
        return optChem['X_H'] * abund(i,ids) * const.orderAtomicWeight[i] * masses[ids]

    elif name in const.orderRates:               # Ionization rates
        i = const.orderRates.index(name)
        rates = fileSnap[pt]['PhotonRates'][:,i]
        return rates[ids]

    elif name in nameStd:
        values = fileSnap[pt][name][:]
        return values[ids]

    else:
        return None
