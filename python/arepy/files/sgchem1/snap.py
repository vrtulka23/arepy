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
