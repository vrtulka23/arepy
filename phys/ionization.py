import numpy as np
import arepy.constants as const

# Stromgren ionization tests
# Baczynsky 2015
class IonizationFrontTest:
    def __init__(self, n=1e-3, Q=1e49, T_avg=1e4, a=2.7e-13, mu=1, gamma=5./3.):
        self.n = n              # n [1/cm^3]     number density
        self.Q = Q              # Q [1/s]        production rate of photons in the source
        self.T_avg = T_avg      # T_i [K]        average temperature in the ionized gas
        self.a = a              # a [cm^3/s]     recombination factor
        self.mu = mu            # mu [g]         mean molecular weight of the gas
        self.gamma = gamma      # gamma          polytropic index for the gas
        
        # Stromgren radius [cm]
        self.r_st = ( ( 3.*self.Q ) / ( 4.*np.pi*(self.n*self.mu)**2*self.a) )**(1./3.)
        
        # Recombination time [s]
        self.t_rec = 1. / ( self.a*self.n )

        # Speed of sound in a gas [cm/s]
        self.c_s = np.sqrt( ( self.gamma*const.k_B*self.T_avg ) / ( self.mu*const.m_p ) )

    # R-type ionization front expansion
    #   t [s]   time
    def r_R(self,t):
        return self.r_st * ( 1. - np.exp(-1.*t/self.t_rec) ) ** (1./3.)
        
    # D-front ionization front expansion
    # Hosokawa & Inutskuka 2006
    #   t [s]   time
    def r_D(self,t):
        return self.r_st * ( 1. + np.sqrt( 4./3. ) * ( 7.*self.c_s*t ) / ( 4.*self.r_st ) ) ** (4./7.)

    # Spitzer radius [cm]
    # Spitzer 1978
    #   t [s]          time
    def r_sp(self,t):
        return self.r_st * ( 1. + ( 7.*self.c_s*t ) / ( 4.*self.r_st ) ) ** (4./7.)

    # Spitzer time [s]
    # Spitzer 1978
    #   r [cm]         radius
    def t_sp(self,r):
        return ( ( r/self.r_st )**( 7./4. ) - 1. ) * ( 4.*self.r_st ) / ( 7.*self.c_s )
    

# Test of Direct Pressure from Ionising Radiation
# Rosdahl & Teyssier 2015
class RadiationPressureTest:
    
    def __init__(self, a, n, L, E, T_i, T_o, r_st):
        self.a = a       # a [cm^3/s]     recombination factor
        self.n = n       # n [1/cm^3]     number density
        self.L = L       # L [erg/s]      source luminosity
        self.E = E       # E [erg]        mean photon energy
        self.T_i = T_i   # T_i [K]        temperature in the ionized bubble
        self.T_o = T_o   # T_o [K]        external temperature
        self.r_st = r_st # r_st [cm]      Stromgren radius
        
        # Radiation pressure radius [cm]
        self.r_gamma = np.sqrt( self.L / (4. * np.pi * const.c * self.n * const.k_B * self.T_o) )

        # Photo-Ionization heating radius [cm]
        self.r_T = ( self.T_i/self.T_o )**(2./3.) * self.r_st
        
