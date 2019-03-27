import numpy as np
from matplotlib import colors
import arepo as arp
from plotting.plotImage import plotImage
from plotting.addColorbar import addColorbar
from utilities.progressBar import progressBar
from utilities.displayImage import displayImage
from utilities.textColor import tc
import matplotlib.pyplot as plt
import h5py as hp
import os.path

# Plot overview of Arepo images
def imageOverview( snapshots, outputDir='output', imageType='proj', 
                       properties=['density','temp'], resultsDir='results', figPrefix='figOverview_',
                       labels=('x','y'), extent=(0,1,0,1), plotSize=[3.5,3.0], 
                       cmap=None, imageSize=(1000,1000), show=False ):

    print tc('Plotting snapshots %d-%d'%(min(snapshots),max(snapshots)),'green')

    if len(np.array(properties).shape)==2:
        nRows = np.array(properties).shape[0]
        nCols = np.array(properties).shape[1]
        properties = np.array(properties)
    else:
        nRows = 1
        nCols = np.array(properties).shape[0]
        properties = np.array([properties])

    nSnaps = len(snapshots)

    prog = progressBar(maxValue=nRows*nCols*nSnaps+nRows*nCols,label="Reading data")

    image = np.zeros((nRows,nCols,nSnaps,imageSize[0],imageSize[1]))
    for r in range(nRows):
        for c in range(nCols):
            for s in range(nSnaps):
                if properties[r][c][:7] == 'sxrates':
                    rate = int(properties[r][c][7])
                    fileName = '%s/%s_%s_%03d'%(outputDir,'sxrates',imageType,snapshots[s])
                    im, px, py = arp.files.image( fileName, size=nChemRates, select=rate )
                else:
                    fileName = '%s/%s_%s_%03d'%(outputDir,properties[r][c],imageType,snapshots[s])
                    im, px, py = arp.files.image( fileName )
                image[r,c,s,:] = im
                prog.increase()
                
    vmin = np.zeros((nRows,nCols))
    vmax = np.zeros((nRows,nCols))
    for r in range(nRows):
        for c in range(nCols):
            vmin[r,c] = image[r,c,:].min()
            vmax[r,c] = image[r,c,:].max()
    prog.increase(nRows*nCols)

    prog.close()

    if not os.path.exists(resultsDir):
        os.makedirs(resultsDir)

    prog = progressBar(maxValue=nRows*nCols*nSnaps,label="Plotting")

    for s, snap in enumerate(snapshots):
        fig = plt.figure(figsize=(nCols*plotSize[0], nRows*plotSize[1]))
        for r in range(nRows):
            for c in range(nCols):
                ax = fig.add_subplot( nRows, nCols, r*nCols+c+1 )
                if properties[r][c] in ['density']:
                    norm = colors.LogNorm(vmin=vmin[r,c],vmax=vmax[r,c])
                else:
                    norm = colors.Normalize(vmin=vmin[r,c],vmax=vmax[r,c])
                im = plotImage( ax, image[r,c,s], title=properties[r,c],
                                labels=labels, extent=extent, norm=norm, cmap=cmap)
                addColorbar(im)
                #plt.colorbar(im)
                prog.increase()

        snapFile = '%s/snap_%03d.hdf5'%(outputDir,snapshots[s])
        if not os.path.isfile(snapFile):
            snapFile = '%s/snapdir_%03d/snap_%03d.0.hdf5'%(outputDir,snapshots[s],snapshots[s])
        with hp.File(snapFile) as f:
            time = f['Header'].attrs['Time']

        plt.suptitle('Time = %f'%time)
        plt.tight_layout()
        plt.savefig( resultsDir+'/%s%03d.png'%(figPrefix,snap) )
        plt.close(fig)
        
    prog.close()

    if show:
        displayImage(fileName='%s*'%(figPrefix))
