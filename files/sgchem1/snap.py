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

    def abund(i,ids):
        if i<6:
            abund = fileSnap[pt]['ChemicalAbundances'][:,i]
            return abund[ids]
        elif i==6: # x_H
            x_H2 = fileSnap[pt]['ChemicalAbundances'][:,0]
            x_HP = fileSnap[pt]['ChemicalAbundances'][:,1]
            x_HD = fileSnap[pt]['ChemicalAbundances'][:,3]
            return optChem['x0_H']  - 2*x_H2[ids] - x_HP[ids]- x_HD[ids]
        elif i==7: # x_He
            x_HEP = fileSnap[pt]['ChemicalAbundances'][:,4]
            x_HEPP = fileSnap[pt]['ChemicalAbundances'][:,5]
            return optChem['x0_He'] - x_HEP[ids]  - x_HEPP[ids]
        elif i==8: # x_D
            x_DP = fileSnap[pt]['ChemicalAbundances'][:,2]
            x_HD = fileSnap[pt]['ChemicalAbundances'][:,3]
            return optChem['x0_D']  - x_DP[ids]   - x_HD[ids]
        
    if name in const.orderPhotonFlux:          # Photon Flux in a particular bin
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
