import numpy as np
import arepy as apy

# Starbench tests
# Bisbas et al. 2015
#
# Settings in the paper:
#   alpha_B = 2.7e-13
#   N_dot = 1e49
#   c_o = 0.91e5  (cm/s)  for the early phase with T_0=10^2 K
#   c_o = 2.87e5  (cm/s)  for the late phase with  T_0=10^3 K
#   c_i = 12.85e5 (cm/s)
#   rho_o = 5.21e-21
#
# Calculation for a purely Hydrogen gas and isotermal equation of state

class StarbenchTests:
    def __init__(self, alpha_B=2.7e-13, N_dot=1e49, c_o=2.87e5, c_i=12.85e5, rho_o=5.21e-21):
        self.alpha_B = alpha_B  # alpha_B [cm^3/s]     recombination factor
        self.N_dot = N_dot      # N_dot [1/s]          production rate of photons in the source
        self.c_o = c_o          # c_o [cm/s]           sound speed in the neutral gas
        self.c_i = c_i          # c_i [cm/s]           sound speed in the ionized gas
        self.rho_o = rho_o      # rho_o [g/cm^3]       initial density of the gas
        
        # Stromgren Radius [cm]
        self.r_st = ( ( 3.*self.N_dot*apy.const.m_p**2 ) / ( 4.*np.pi*self.alpha_B*self.rho_o**2 ) ) ** (1./3.)

        self.n = self.rho_o/apy.const.m_p          # Number density of hydrogen [1/cm^3]
        self.t_rec = 1. / ( self.alpha_B*self.n )  # Recombination time in [s]

        self.r_fi  = self.r_st * ( self.c_i/self.c_o )**(4./3.)                      # Stagnation radius Raga-I
        self.r_fii = self.r_st * (8./3.)**(2./3.) * ( self.c_i/self.c_o )**(4./3.)   # Stagnation radius Raga-II

    # Sound speed calculation
    # mu=0.5 for ionized (1e4 K) and mu=1 for neutral (1e2, 1e3 K) gas
    def c_s(self,T_gas=1e4,mu=0.5,gamma=1):
        return np.sqrt( apy.const.k_B * T_gas / ( mu * apy.const.m_p ) )

    # Solution of Spitzer 1978
    def r_sp(self, t): # time (s)
        return self.r_st * ( 1. + ( 7.*self.c_i*t ) / ( 4.*self.r_st ) ) ** ( 4./7. )  # radius (cm)

    # Solution of Hosokawa & Inutsuka 2006
    def r_hi(self, t): # time (s)
        return self.r_st * ( 1. + np.sqrt(4./3.) * ( 7.*self.c_i*t ) / ( 4.*self.r_st ) ) ** (4./7.)  # radius (cm)

    # The universal time-evolution of expanding HII
    # Raga et al. 2012a, Equations 24-26
    def r_rg(self, tau):        
        f1 = (7./(2.*np.sqrt(3))*tau)**(4./7.)
        f2 = 1.-(1.-2.2*tau+4.2*tau*tau-3.3*tau*tau*tau)*np.exp(-2.4*tau)
        return np.exp(-10.*tau)*f1+(1.-np.exp(-10.*tau))*f2

    # Raga's extension of Spitzer (Raga-I)
    def r_rgi(self, t): # time (s)
        tau = t * self.c_o / self.r_fi
        return self.r_rg(tau) * self.r_fi # radius (cm)

    # Raga's extension of Hosokawa-Inutsuka (Raga-II)
    # DEBUG: this gives slightly different results like in the Starbench, needs some more thinking
    def r_rgii(self, t): # time (s)
        tau = t * self.c_o / self.r_fii
        return self.r_rg(tau) * self.r_fii # radius (cm)

    def line(self,which=None,fileName='output.dat'):
        data = np.loadtxt(apy.settings['arepy']+'/phys/starbench/'+fileName,skiprows=1).T
        header = ['step','time','Spitzer','Hosokawa-Inutsuka','Raga-I','Raga-II','StarBench']
        lines = {'time':1,'r_sp':2,'r_hi':3,'r_rgi':4,'r_rgii':5,'r_sb':6}
        if isinstance(which,str):
            i = lines[which]
            return data[i]
        elif isinstance(which,int):
            return data[which]
        else:
            for key,val in lines.items():
                lines[key] = data[val]
            return lines

    '''
    # Raga's extension of Hosokawa-Inutsuka (Raga-II)
    # DEBUG: this is an attemt to use equation (11) from the Raga et al. 2012b
    def r_rgii(self, t):
        r_stag = self.r_st * (8./3.)**(2./3.) * ( self.c_i/self.c_o )**(4./3.)
        tau = t * self.c_o / r_stag
        return tau**(1./3.) * r_stag
    '''
