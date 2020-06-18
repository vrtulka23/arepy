import numpy as np
import arepy as apy

# Radiation pressure equation from
# Rosdahl&Teyssier 2015
class RadiationPressureTest:
    def __init__(self, Q, alphaB, n, T_ion, T_0, E_gamma):
        
        self.Q = Q              # ph/s
        self.alphaB = alphaB    # cm^3/s
        self.n = n              # cm^-3
        self.T_ion = T_ion      # K
        self.T_0 = T_0          # K
        self.E_gamma = E_gamma  # erg

        # derived values
        self.L = Q * E_gamma          # erg/s
        self.rho = n * apy.const.m_p  # g/cm^3

        # equation 60 (cm)
        self.r_st = ( (3*Q) / (4*np.pi*alphaB*n**2) )**(1./3.)

        # equation 62 (cm)
        self.r_gamma = ( (Q*E_gamma) / (4*np.pi*apy.const.c*n*apy.const.k_B*T_0) )**(1./2.)

        # equation 65 (cm)
        self.r_T = (T_ion/T_0)**(2./3.) * self.r_st

        # equation 67 (Q when r_gamma==r_T)
        self.Q_equal = (1./n) * (T_ion**4/T_0) * (36*np.pi*apy.const.c**3*apy.const.k_B**3) / (alphaB**2*E_gamma**3)

    # equation 59 (cm)
    def r_dfront(self,t): 
        A = 3*self.L / (4*np.pi*self.rho*apy.const.c)
        return (self.r_st**4 + 2*A*t**2)**(1/4)
