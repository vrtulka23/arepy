import numpy as np
import scipy as scp
import arepy as apy
import arepy.constants as const

# This function integrates gravitational potential from the mass in the sphere
# using given radial density profile
# https://en.wikipedia.org/wiki/Gravitational_potential
def GravPot(self, fnRho, radius):
    def fnGravPot(r):
        return apy.const.G * 4 * np.pi * fnRho(r) * r
    if np.isscalar(radius):
        return scp.integrate.quad(fnGravPot, 0, radius)
    else:
        return np.array([scp.integrate.quad(fnGravPot, 0, r) for r in radius])
