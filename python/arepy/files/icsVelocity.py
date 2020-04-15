import arepy as apy
import numpy as np

class icsVelocity:

    def getTurbulence(self,nx,dirSim):
        fileName = dirSim+'/velocity%d.npy'%nx
        if apy.shell.isfile(fileName):
            apy.shell.printc('Reading from: '+fileName)
            return np.load(fileName)

        p = -4. #-4.   #-11. / 3.
        
        # Wave vectors
        k1_alias = np.arange(nx, dtype=np.float64)
        k1 = np.where(k1_alias >= nx / 2, k1_alias - nx, k1_alias)
        kx, ky, kz = np.meshgrid(k1, k1, k1)
        k = np.sqrt(kx**2 + ky**2 + kz**2)
        # Phase
        phx = np.exp(2. * np.pi * 1j * np.random.random((nx, nx, nx)))
        phy = np.exp(2. * np.pi * 1j * np.random.random((nx, nx, nx)))
        phz = np.exp(2. * np.pi * 1j * np.random.random((nx, nx, nx)))
        # Amplitude
        ax = np.sqrt(-2. * np.log(np.random.random((nx, nx, nx)))) * k**(p/2.)
        ay = np.sqrt(-2.  * np.log(np.random.random((nx, nx, nx)))) * k**(p/2.)
        az = np.sqrt(-2. * np.log(np.random.random((nx, nx, nx)))) * k**(p/2.)
        # Fourier coefficients
        vxf = phx * ax
        vyf = phy * ay
        vzf = phz * az
        # Remove NaNs at origin
        vxf[0, 0, 0] = 0.
        vyf[0, 0, 0] = 0.
        vzf[0, 0, 0] = 0.
        # Inverse transform
        vx = np.fft.fft(vxf)
        vy = np.fft.fft(vyf)
        vz = np.fft.fft(vzf)
        # Keep only real part
        vx = np.real(vx)
        vy = np.real(vy)
        vz = np.real(vz)
        v = np.array([vx.flatten(),vy.flatten(),vz.flatten()]).T
        v = v.astype(np.float64)
        
        np.save(fileName,v)
        apy.shell.printc('Saving as: '+fileName)
        return v
        
    def useTurbulence(self,nx,alpha,dirSim):
        
        v = self.getTurbulence(nx,dirSim)
        vx,vy,vz = v.T

        #####
        # start with mass weighting to derive the average velocity and the standard deviation
        #####

        new_mass_cgs = self.masses * self.units['mass']
        mass_total = (new_mass_cgs).sum()
        dens_outer_radius  = 5.763e18    #1.8 pc [cm]

        #####
        # mass weighted average velocity and the standard deviation
        #####

        # average velocity
        vx_tot = (vx * new_mass_cgs).sum() / mass_total
        vy_tot = (vy * new_mass_cgs).sum() / mass_total
        vz_tot = (vz * new_mass_cgs).sum() / mass_total
        
        # standard deviation
        vx2_tot = (vx**2. * new_mass_cgs).sum() / mass_total    
        vy2_tot = (vy**2. * new_mass_cgs).sum() / mass_total
        vz2_tot = (vz**2. * new_mass_cgs).sum() / mass_total
        
        # velocity cm/s
        v_rms0 = np.sqrt(0.73 * alpha * apy.const.G * mass_total / dens_outer_radius )
        v_rms11 = np.sqrt(vx2_tot-vx_tot**2 + vy2_tot-vy_tot**2 + vz2_tot-vz_tot**2)
        v_rms = v_rms0 / v_rms11
        
        vx_new = v_rms * (vx - vx_tot)
        vy_new = v_rms * (vy - vy_tot)
        vz_new = v_rms * (vz - vz_tot)
 
        #print(vx_tot, vx2_tot, v_rms)
                                       
        f = {'PartType0/Velocities':np.zeros_like(v)}
        f["PartType0/Velocities"][:,0] = vx_new / self.units['velocity']
        f["PartType0/Velocities"][:,1] = vy_new / self.units['velocity']
        f["PartType0/Velocities"][:,2] = vz_new / self.units['velocity']
        
        self.velocities = f['PartType0/Velocities'][:]
        
        #print(f)
