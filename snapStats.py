import h5py as hp
import numpy as np
from utilities.textColor import tc
from utilities.findFiles import findFiles
import arepo.constants as const
from tabulate import tabulate
from utilities.progressBar import progressBar

def snapStats(properties=['snap','redshift','time','min_ppc','mean_ppc','max_ppc','nType5','nType0'], 
               headers=['#','z','a','min ppc','mean ppc','max ppc','nSinks','nGas'], 
               outputDir='output',snaps=[]):

    if snaps==[]:
        snaps = findFiles( 'output', 'snap_([0-9]+).hdf5', dtParam=int )

    nSnaps = len(snaps)
    nProps = len(properties)
    data = np.zeros((nSnaps,nProps))

    pb = progressBar(maxValue=nSnaps, label="Reading snapshot")

    for s, snap in enumerate(snaps):
        snapFile = '%s/snap_%03d.hdf5'%(outputDir,snap)
        with hp.File(snapFile,'r') as f:
            dens = f['PartType0/Density'][:]
            nGas = f['Header'].attrs['NumPart_Total'][0]
            nSinks = f['Header'].attrs['NumPart_Total'][5]
            a = f['Header'].attrs['Time']
            h = f['Header'].attrs['HubbleParam']
            U_m = f['Header'].attrs['UnitMass_in_g']
            U_l = f['Header'].attrs['UnitLength_in_cm']
            dens2 = dens * (h**2 / a**3) * (U_m / U_l**3) / (const.m_p * (1+4*const.x_He))
            redshift = f['Header'].attrs['Redshift']
            data[s] = [snap, redshift, a, dens2.min(), dens2.mean(), dens2.max(), nSinks, nGas]
        pb.increase()

    pb.close()

    print( tabulate(data,headers=headers, tablefmt="orgtbl") )
