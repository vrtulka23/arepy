import numpy as np
import arepy as apy
import matplotlib.pyplot as plt
import h5py as hp
import subprocess

class comparison:

    def __init__(self,grid=(1,1),subPlotSize=(3.0,3.5),dirResults='results',fileNameFigure='figOverview%s.png'):
        
        self.grid = grid
        self.subPlotSize = subPlotSize
        self.dirResults = dirResults
        self.fileNameFigure = fileNameFigure

        # setup norms
        self.norms = apy.plot.norms()

        # create subplots
        self.nSubplot = grid[0]*grid[1]
        self.pb = apy.util.pb(maxValue=self.nSubplot, label='Reading values')
        self.subplot = [apy.plot.subplot(self,a) for a in range(self.nSubplot)]

    def plot(self,movie=False,fileNameMovie="figOverview.mp4"):
        self.pb.close()

        # delete previous figures        
        fileNameFigures = self.dirResults+'/'+self.fileNameFigure%'*'
        subprocess.call("rm -f %s"%fileNameFigures, shell=True ) 

        # plot new figures
        nFigures = np.min([sp.nSnap for sp in self.subplot])
        with apy.util.pb(maxValue=nFigures*self.nSubplot, label="Plotting figures") as pb: 
            for f in range(nFigures):
                fig = plt.figure(figsize=(self.grid[1]*self.subPlotSize[1], self.grid[0]*self.subPlotSize[0]))
                for a in range(self.nSubplot): 
                    ax = fig.add_subplot( self.grid[0], self.grid[1], a+1 )
                    self.subplot[a].plot(fig,ax,f)
                    pb.increase()
                plt.tight_layout()
                fileFig = self.dirResults+'/'+self.fileNameFigure%('%03d'%f)
                plt.savefig( fileFig )
                plt.close(fig)
        
        if movie:
            fileNameMovie = self.dirResults+'/'+fileNameMovie
            apy.util.makeMovie(fileNameMovie,fileNameFigures)

    def show(self):
        fileName = self.dirResults+'/'+self.fileNameFigure%'*'
        apy.util.displayImage(fileName=fileName)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        True
