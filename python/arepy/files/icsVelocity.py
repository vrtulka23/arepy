import arepy as apy
import numpy as np

class icsVelocity:

    def useTurbulence():
        nx = 128 
        p = -4. #-4.   #-11. / 3.
        
        # Wave vectors
        k1_alias = np.arange(nx, dtype=np.float64)
        k1 = np.where(k1_alias >= nx / 2, k1_alias - nx, k1_alias)
        kx, ky, kz = np.meshgrid(k1, k1, k1)
        k = np.sqrt(kx**2 + ky**2 + kz**2)
        
        
        # Phase
        phx = np.exp(2. * np.pi * 1j * npr.random((nx, nx, nx)))
        phy = np.exp(2. * np.pi * 1j * npr.random((nx, nx, nx)))
        phz = np.exp(2. * np.pi * 1j * npr.random((nx, nx, nx)))
        
        
        # Amplitude
        ax = np.sqrt(-2. * np.log(npr.random((nx, nx, nx)))) * k**(p/2.)
        ay = np.sqrt(-2. * np.log(npr.random((nx, nx, nx)))) * k**(p/2.)
        az = np.sqrt(-2. * np.log(npr.random((nx, nx, nx)))) * k**(p/2.)
        
        
        # Fourier coefficients
        vxf = phx * ax
        vyf = phy * ay
        vzf = phz * az
        
        
        # Remove NaNs at origin
        vxf[0, 0, 0] = 0.
        vyf[0, 0, 0] = 0.
        vzf[0, 0, 0] = 0.
        
        #print vxf.ndim
        #print vxf.shape
        
        
        # Inverse transform
        vx = ifftn(vxf)
        vy = ifftn(vyf)
        vz = ifftn(vzf)
        
        #print vx.shape
        
        # Keep only real part
        vx = np.real(vx)
        vy = np.real(vy)
        vz = np.real(vz)
        
        #print vx.shape
        
        
        v = np.array([vx.flatten(),vy.flatten(),vz.flatten()]).T
        #print v.shape
        #print len(v[:,1])
        #print len(v[:,2])
        #print len(v[3:,])
        #print (v[3:,])
        v = v.astype(np.float64)
        
        # Save cube
        #hdf5out = True
        #if hdf5out:
        #    h5fd = T.open_file("turbulencecube.hdf5", mode='w')
        #    h5fd.create_array("/", "Velocities",v)
        #    h5fd.create_array("/", "nx", nx)
        #    h5fd.create_array("/", "vx", vx)
        #    h5fd.create_array("/", "vy", vy)
        #    h5fd.create_array("/", "vz", vz)
        #    h5fd.close()

        return v
