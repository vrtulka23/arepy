import numpy as np
import arepy as apy

from scipy.integrate import odeint

# Williams et al. 2018
# Parameter free solution of the D-type expansion
#
# ODE integration adapted from
# https://stackoverflow.com/questions/19779217/need-help-solving-a-second-order-non-linear-ode-in-python

class williams:

    def __enter__(self):
        return self
    def __exit__(self, type, value, tb):
        return
    def __init__(self,**opts):

        # initial
        self.rho0 = 5.21e-21    # g/cm^3
        self.Q0 = 1e49          # s^-1
        self.Q0dot = 0          # s^-2
        #self.Ti = 1e4           # K
        #self.T0 = 1e2           # K
        #self.nui = 0.5          
        #self.nu0 = 1 
        self.ci = 12.85 * apy.const.km   # km/s
        self.c0 = 0.91 * apy.const.km    # km/s
        self.alpha_B = 2.7e-13  # cm^3/s

        for key in opts:
            setattr(self, key, opts[key])

        # Stromgren radius (0.314 pc)
        self.Rst = ( (3*self.Q0*apy.const.m_p**2) /\
                     (4*np.pi*self.alpha_B*self.rho0**2) )**(1/3) 
        # stagnation radius (10.75 pc)
        self.Rstag = (self.ci/self.c0)**(4/3) * self.Rst  

        # parameters
        self.beta = (1-self.c0**2/self.ci**2) # ~1
        self.C = 2.25
        self.B = (1+self.beta)/2 

    def show(self):
        print('rho0 %.03e'%self.rho0)
        print('ci   %.03e  c0      %.03e'%(self.ci,self.c0))
        print('Q0   %.03e  Q0dot   %.03e'%(self.Q0,self.Q0dot))

    def _differential(self,z,t):
        # defining z=[r',r] and z'=[r'',r']
        part1  = -1 * (self.beta * (7-self.beta) * z[0]**2) / 2
        part2  = -1 * (3*z[0]*self.c0) / (2 * (1+self.C*z[0]**2/self.c0**2))
        part31 = self.c0**2 * (self.c0 + 3*self.B*z[0]) / (self.c0 + self.B*z[0])
        part32 = (self.Rstag/z[1])**(3/2) - 1
        part4  = (self.c0*z[1]*self.Q0dot) / (2*self.Q0)
        return np.array((
            (part1+part2+part31*part32+part4)/(self.beta*z[1]),  # this is z'[0]
            z[0]                                                 # this is z'[1]
        ))

    def calculate(self,**opts):

        self.t = np.linspace(0,200,200) * apy.const.Myr  # time (s)
        self.r0 = [self.c0*0.01, 0.01*self.Rstag]  # initial conditions from the Figure 4
        
        # set parameters
        for key in opts:
            setattr(self, key, opts[key])

        _,self.r = odeint(self._differential, self.r0, self.t).T    # radius (cm)

        return self.t,self.r
        
