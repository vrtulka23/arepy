mf0H = 0.752         # Initial H mass fraction
mf0He = 0.248        # Initial He mass fraction
orderElem= ['Carbon', 'Helium', 'Hydrogen', 'Iron', 'Magnesium', 'Neon', 'Nitrogen', 'Oxygen', 'Silicon']
orderElemA=[12.0,     4.0,      1.0,        55.8,   24.3,        20.2,    14.0,      16.0,     28.1]
orderMassFract=['X_D+', 'X_H+', 'X_H-', 'X_H2', 'X_H2+', 'X_HD', 'X_He+', 'X_He++']
dsets = {'ElementAbundance':9,'MassFractions':8}
imageTypes=[]

import numpy as np
import arepy as apy
from arepy.files.fiby import constants as const

def getHeader(fileSnap,name):
    if name in ['UnitMass_in_g','UnitLength_in_cm','UnitVelocity_in_cm_per_s']:
        return fileSnap['Units'].attrs[name]
    elif name=='ExpansionFactor':
        return fileSnap['Header'].attrs['ExpansionFactor']

def getProperty(fileSnap,ptype,name,ids,comoving):
    pt = 'PartType%d'%ptype

    nameStd = ['Mass','Velocity']

    def unitDensity():
        unitMass = fileSnap['Units'].attrs['UnitMass_in_g']
        unitLength = fileSnap['Units'].attrs['UnitLength_in_cm']
        if comoving:
            h = fileSnap['Header'].attrs['HubbleParam']
            a = fileSnap['Header'].attrs['ExpansionFactor']
            density2cgs = ( unitMass * h**2 ) / (a * unitLength )**3
        else:
            density2cgs = unitMass / unitLength**3
        return density2cgs
    
    def calcMu():
        invElemA = 1./np.array(const.orderElemA)
        elem = [ fileSnap[pt]['ElementAbundance'][o][:] for o in const.orderElem ] 
        ionDp = fileSnap[pt]['MassFraction_D+'][:]
        ionHp = fileSnap[pt]['MassFraction_H+'][:]
        ionH2p = fileSnap[pt]['MassFraction_H2+'][:]
        ionHep = fileSnap[pt]['MassFraction_He+'][:]
        ionHepp = fileSnap[pt]['MassFraction_He++'][:]
        ionHm = fileSnap[pt]['MassFraction_H-'][:]
        elmHD = fileSnap[pt]['MassFraction_HD'][:]
        elmH2 = fileSnap[pt]['MassFraction_H2'][:]
        nspecies = np.sum([ elem[i][ids]*invElemA[i] for i in range(const.dsets['ElementAbundance']) ],axis=0)
        #nspecies += elmHD[ids]/3.0 + elmH2[ids]*0.5  # not sure if this is already included
        nelectrons = ionDp[ids] + ionHp[ids] + ionH2p[ids] + ionHep[ids] + 2.0*ionHepp[ids] - ionHm[ids]
        return 1. / ( nspecies + nelectrons )
    
    if name=='Mu':      # in units of the proton mass
        return calcMu()

    elif name=='Temperature':            # in physical [K]
        nu = calcMu()
        utherm = fileSnap[pt]['InternalEnergy'][ids] *\
            fileSnap['Units'].attrs['UnitVelocity_in_cm_per_s']**2
        return utherm * apy.const.m_p / apy.const.k_B * ( apy.const.gamma - 1. ) * nu 

    elif name=='Temperature2':
        return fileSnap[pt]['Temperature'][ids]

    elif name=='NumberDensity':             # in physical [1/cm^3]
        dens = fileSnap[pt]['Density'][:]
        return dens[ids] * unitDensity() / ( apy.const.m_p * calcMu() )
    
    elif name=='NumberDensityH':
        dens = fileSnap[pt]['Density'][:]
        mf = fileSnap[pt]['ElementAbundance']['Hydrogen'][:]
        return (dens[ids] * mv[ids]) * unitDensity() / ( apy.const.m_p * calcMu() )

    elif name in const.orderElem:        # mass fraction
        mf = fileSnap[pt]['ElementAbundance'][name][:]
        return mf[ids]

    elif name in const.orderMassFract:   # mass fraction
        mf = fileSnap[pt]["MassFraction_"+name][:]
        return mf[ids]

    elif name in nameStd:
        values = fileSnap[pt][name][:]
        return values[ids]

    else:
        return None
