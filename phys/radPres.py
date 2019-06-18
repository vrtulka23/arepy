import numpy as np
import arepy.constants as const

# Radiation pressure equation from
# Rosdahl&Teyssier 2015
class RadiationPressureTest:
    def __init__(self, Q, a, n, T_ion, T_0, E_gamma):
        
        # equation 60.
        self.r_st = ( (3*Q) / (4*np.pi*a*n**2) )**(1./3.)

        # equation 62.
        self.r_gamma = ( (Q*E_gamma) / (4*np.pi*apy.const.c*n*apy.const.k_B*T_0) )**(1./2.)

        # equation 65.
        self.r_T = (T_ion/T_0)**(2./3.) * self.r_st

        # equation 67. (Q when r_gamma==r_T)
        self.Q_equal = (1./n) * (T_ion**4/T_0) * (36*np.pi*apy.const.c**3*apy.const.k_B**3) / (a**2*E_gamma**3)
