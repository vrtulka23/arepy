import numpy as np
import arepy.constants as const

# Jean theory of gravitational collapse
# from book: Carroll & Ostile, An Introduction to Modern Astrophysics, pg. 456
class JeansTheory:
    def __init__(self,n,T,mu=1):
        self.n = n       # n [1/cm^3]     gas number density
        self.T = T       # T [K]          gas temperature
        self.mu = mu     # mu [g]         gas mean molecular weight

        # Jeans mass [g]
        self.M_j = ( ( 4*const.k_B*self.T ) / ( const.G*const.m_p*self.mu ) )**(3./2.) * \
                   np.sqrt( 3. / ( 4.*np.pi*self.n*self.mu*const.m_p ) )

        # Jeans length [cm]
        self.R_j = np.sqrt( ( 15.*const.k_B*self.T ) / \
                            ( 4.*np.pi*const.G*self.mu*const.m_p*self.n*self.mu*const.m_p) )
        
        # Free fall time [s]
        self.t_ff = np.sqrt( ( 3.*np.pi ) / ( 32.*const.G*self.n*self.mu*const.m_p) )
