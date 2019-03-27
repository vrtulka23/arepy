from matplotlib import colors
import arepy as apy
import matplotlib.pyplot as plt
import h5py as hp
import os.path
import numpy as np

class overview:
    
    def __init__( self, snapshots=None, imageDim=(1000,1000),
                  outputDir='output', resultsDir='results', snapPrefix="snap_", fileParam="param.txt",
                  plotSize=(3.5,3.0), cmap=None, boxCoord=None, codeUnits=None ):

        self.images = []
        self.particles = []
        self.circles = []
        self.outputDir = outputDir
        self.resultsDir = resultsDir
        self.snapPrefix = snapPrefix
        self.imageDim = imageDim
        self.plotSize = plotSize
        self.cmap = cmap

        if snapshots==None:
            snapshots = apy.util.findFiles( self.outputDir, 'density_proj_([0-9]+)', dtParam=int )
        self.snapshots = snapshots
        self.nSnapshots = len(snapshots)

        print apy.util.textColor('Creating image overview from %d snapshots...'%self.nSnapshots,'green')

        self.snapFiles = []
        for snap in self.snapshots:
            snapFile = '%s/snap_%03d.hdf5'%(self.outputDir,snap)
            if not os.path.isfile(snapFile):
                snapFile = '%s/snapdir_%03d/snap_%03d.0.hdf5'%(self.outputDir,snap,snap)
            self.snapFiles.append( snapFile )

        pf = apy.files.param(fileParam)

        self.boxCoord = boxCoord
        if self.boxCoord==None:
            self.boxCoord = [ pf.params['PicXmin']['value'], pf.params['PicXmax']['value'],
                              pf.params['PicYmin']['value'], pf.params['PicYmax']['value'],
                              pf.params['PicZmin']['value'], pf.params['PicZmax']['value'] ]
        self.codeUnits = codeUnits
        if self.codeUnits==None:
            self.codeUnits = {"length": pf.params['UnitLength_in_cm']['value'],
                          "mass": pf.params['UnitMass_in_g']['value'],
                          "velocity": pf.params['UnitVelocity_in_cm_per_s']['value']}
        self.codeUnits['time'] = self.codeUnits['length'] / self.codeUnits['velocity']

        if not os.path.exists(resultsDir):
            os.makedirs(resultsDir)
        
    def plotFigures(self, grid=None, figPrefix="figOverview_", 
                    labels=('x (pc)','y (pc)'), units={}):

        nImages = len(self.images)

        prog = apy.util.pb(vmax=nImages*self.nSnapshots,label="Plotting figures")

        if grid==None:
            sqrt = np.sqrt(nImages)
            grid = ( np.ceil(sqrt), np.floor(sqrt) )

        conv = {}
        for key,value in self.codeUnits.items():
            conv[key] = value/units[key] if key in units else 1.0

        imgrad = (self.boxCoord[1] - self.boxCoord[0]) * 0.5

        for s, snap in enumerate(self.snapshots):
            with hp.File(self.snapFiles[s],'r') as f:
                time = f['Header'].attrs['Time']

            fig = plt.figure(figsize=(grid[1]*self.plotSize[0], grid[0]*self.plotSize[1]))
            axes = []
            for g in range(grid[0]*grid[1]):
                axes.append( fig.add_subplot( grid[0], grid[1], g+1 ) )

            for circle in self.circles:
                ax = axes[ circle['axis'] ]
                shape = plt.Circle( circle['center'], circle['radius'], 
                                    linestyle=circle['linestyle'],
                                    color=circle['color'], fill=False)
                ax.add_artist(shape)

            for particle in self.particles:
                ax = axes[ particle['axis'] ]
                center = (np.array(self.boxCoord[::2])+np.array(self.boxCoord[1::2])) * 0.5
                coords = (particle['coords'][s]-center) * conv['length']
                ax.scatter( coords[:,0], coords[:,1], marker=particle['marker'], color=particle['color'] )

            for image in self.images:
                ax = axes[ image['axis'] ]
                
                if image['property'] in ['density']:
                    norm = colors.LogNorm(vmin=image['vminpos'],vmax=image['vmax'])
                else:
                    norm = colors.Normalize(vmin=image['vmin'],vmax=image['vmax'])

                    extent = np.array([ -imgrad, imgrad, -imgrad, imgrad ]) * conv['length']
                im = apy.plot.plotImage( ax, image['data'][s], title=image['title'],
                                         labels=(labels['xaxis'],labels['yaxis']), 
                                         extent=extent, norm=norm, cmap=self.cmap)
                apy.plot.addColorbar(im)
                prog.increase()

            plt.suptitle('%s = %f'%(labels['time'],time*conv['time']))
            plt.tight_layout()
            plt.savefig( self.resultsDir+'/%s%03d.png'%(figPrefix,snap) )
            plt.close(fig)

        prog.close()

    def plotMovie(self,fileName="movie.mp4",imgFiles="figOverview_*.png"):
        apy.util.makeMovie(self.resultsDir+'/'+fileName,
                       self.resultsDir+'/'+imgFiles)

    def show(self, figPrefix="figOverview_", ):
        apy.util.displayImage(fileName=self.resultsDir+'/%s*'%(figPrefix))

    def addImages(self, axis, imgProperty, imgType, norm=None, title=None):

        prog = apy.util.pb(vmax=self.nSnapshots,label="Reading %s"%(imgProperty))

        image = {"axis": axis, "property":imgProperty,"type":imgType, 'norm':norm,
                 'data':np.zeros((self.nSnapshots,self.imageDim[0],self.imageDim[1]))}

        image['title'] = imgProperty if title==None else title

        nRates = 6
        for s in range(self.nSnapshots):
            if image['property'][:7] == 'sxrates':
                rate = int(image['property'][7])
                fileName = '%s/%s_%s_%03d'%(self.outputDir,'sxrates',image['type'],self.snapshots[s])
                im, px, py = apy.files.image( fileName, size=nRates, select=rate )
            else:
                fileName = '%s/%s_%s_%03d'%(self.outputDir,image['property'],image['type'],self.snapshots[s])
                im, px, py = apy.files.image( fileName )
            image['data'][s,:] = im
            prog.increase()

        image['vmin'] = image['data'].min()
        image['vminpos'] = image['data'][image['data']>0].min() # this value is used in case of the LogNorm
        image['vmax'] = image['data'].max()

        self.images.append( image )
        
        prog.close()

    def addParticles(self, axis, partType, marker="x", color="black" ):

        prog = apy.util.pb(vmax=self.nSnapshots,label="Reading particle type %d"%(partType))

        particle = {"axis": axis, "type": partType, "marker": marker, "color": color, "coords":[]}

        for s, snap in enumerate(self.snapshots):
            with hp.File(self.snapFiles[s],'r') as f:
                groupName = "PartType%d"%partType
                x = f[groupName]['Coordinates'][:,0]
                y = f[groupName]['Coordinates'][:,1]
                z = f[groupName]['Coordinates'][:,2]
                ids = (self.boxCoord[0]<x)&(x<self.boxCoord[1])& \
                      (self.boxCoord[2]<y)&(y<self.boxCoord[3])& \
                      (self.boxCoord[4]<z)&(z<self.boxCoord[5])
                coords = f[groupName]['Coordinates'][ids,:]
                particle['coords'].append( coords )
            prog.increase()

        self.particles.append( particle )
            
        prog.close()

    def addCircle(self, axis, radius, center=None, color="white", linestyle='-'):
        
        if center==None:
            center = [ (self.boxCoord[1]-self.boxCoord[0])*0.5,
                       (self.boxCoord[3]-self.boxCoord[2])*0.5 ]
        circle = {"axis": axis, "radius": radius, 'center':center, 'color':color, 'linestyle':linestyle} 

        self.circles.append( circle )
