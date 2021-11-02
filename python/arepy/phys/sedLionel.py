import numpy as np
import arepy as apy
import scipy as scp

# Pop III star spectral emition
# from Lionel Haemerle
# iterpolated by Sam Geen 

class sedLionel:

    def __enter__(self):
        return self
    def __exit__(self, type, value, tb):
        return
    def __init__(self,**opts):
        
        fileName = apy.dirScripy+'/pop3/setups/new/popiii_grid_T.dat'
        with open(fileName,'rb',) as f:
            np.fromfile(f, np.int32, 1)    
            ndim = np.fromfile(f, np.int32, 1)
            np.fromfile(f, np.int32, 2)    
            asize = np.fromfile(f, np.int32, 4) 
            np.fromfile(f, np.int32, 2)
            acc = np.fromfile(f, np.float64, asize[0]) - np.log10(apy.const.M_sol/apy.const.yr)
            np.fromfile(f, np.int32, 2)
            mass = np.fromfile(f, np.float64, asize[1]) / apy.const.M_sol
            np.fromfile(f, np.int32, 2)
            axis2 = np.fromfile(f, np.float64, asize[2])
            np.fromfile(f, np.int32, 2)
            axis3 = np.fromfile(f, np.float64, asize[3])
            np.fromfile(f, np.int32, 2)
            data = np.fromfile(f, np.float64, np.prod(asize)).reshape((asize[1],asize[0]))
            self.temp = {
                'temp': data,
                'acc':  acc,
                'mass': mass
            }
            
        fileName = apy.dirScripy+'/pop3/setups/new/popiii_grid_radius.dat'
        with open(fileName,'rb',) as f:
            np.fromfile(f, np.int32, 1)    
            ndim = np.fromfile(f, np.int32, 1)
            np.fromfile(f, np.int32, 2)    
            asize = np.fromfile(f, np.int32, 4) 
            np.fromfile(f, np.int32, 2)
            acc = np.fromfile(f, np.float64, asize[0]) - np.log10(apy.const.M_sol/apy.const.yr)
            np.fromfile(f, np.int32, 2)
            mass = np.fromfile(f, np.float64, asize[1]) / apy.const.M_sol
            np.fromfile(f, np.int32, 2)
            axis2 = np.fromfile(f, np.float64, asize[2])
            np.fromfile(f, np.int32, 2)
            axis3 = np.fromfile(f, np.float64, asize[3])
            np.fromfile(f, np.int32, 2)
            data = np.fromfile(f, np.float64, np.prod(asize)).reshape((asize[1],asize[0]))
            self.rad = {
                'rad': data,
                'acc': acc,
                'mass': mass
            }

    def getTemp(self,mass,acc): # [M_sol], log(M_dot) [M_sol/yr]
        i = np.argmin(np.abs(self.temp['acc']-acc))
        temp = np.interp(
            mass,
            self.temp['mass'],
            self.temp['temp'][:,i]
        )
        print('mass %f acc %f temp %f'%(mass,acc,temp))
        return temp # log(T_eff)  [K]

    def getRad(self,mass,acc): # [M_sol], log(M_dot) [M_sol/yr]
        i = np.argmin(np.abs(self.rad['acc']-acc))
        rad = np.interp(
            mass,
            self.rad['mass'],
            self.rad['rad'][:,i]
        )
        print('mass %f acc %f rad %f'%(mass,acc,rad))
        return rad # log(R)  [R_sol]

    def getIon(self,mass,acc): # [M_sol], log(M_dot) [M_sol/yr]
        
        temp = 10**self.getTemp(mass,acc) # (K)
        rad = 10**self.getRad(mass,acc) * apy.const.R_sol  # (cm)
        # 2/c^2 * star surface [s^2 cm^-2 * cm^2]
        emissionFactor = 2.2253001121e-21 * 4.0 * np.pi * rad * rad;

        # frequency (Hz)
        #fmin = 1.354074682254e15  # 5.6  eV - dust attenuation of photon electric heating radiation
        fmin = 3.28798e15         # 13.6 eV - hydrogen ionisation frequency
        #fmax = 1.3158e16          # 54.4 eV - singly ionised helium ionisation frequency (from Cen 1992)

        photEm, err = scp.integrate.quad(sx_planckDivNu,fmin,fmin*10,args=(temp,))

        # phot/s
        ionRate = photEm * emissionFactor

        print('ionRate', ionRate)
        return ionRate

def sx_planckDivNu( freq, T ):  # B_nu(T)/(h*nu)
    # constant factor 2/c^2 is taken out of the integral
    return freq * freq / (np.exp(apy.const.h * freq / (apy.const.k_B * T)) - 1.0);

