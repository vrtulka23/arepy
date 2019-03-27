import numpy as np
import arepy as apy
from arepy.plot.plot import *
import os

class figure:

    def __init__(self, nRows=1, nCols=1, nFigs=1, **opt):
        
        # initial settings
        self.nRows = nRows     # number of subplots in the row
        self.nCols = nCols     # number of subplots in the column
        self.nFigs = nFigs     # number of figures to plot
        #self.timer = apy.util.timer()
        
        # set options
        self.opt = {
            'debug':      False,
            'dirResults': 'results',
            'dirName':    None,
            'fileName':   'figOverview', 
            'timeStamp':  apy.util.timeStamp(),
            'sRow':       3.0, 
            'sCol':       3.5,
            'nProc':      1,
            'gridspec':   None,
            'fileFormat': 'png',
        }
        self.opt.update(opt)

        if self.opt['nProc']>self.nFigs:
            self.opt['nProc'] = self.nFigs

        if self.opt['debug']:
            apy.shell.printc('Debugging mode is on!!!','r')
            self.opt['timeStamp'] = 'debug'

        dirName = self.opt['fileName'] if self.opt['dirName'] is None else self.opt['dirName']
        self.dirAll = self.opt['dirResults']+'/'+dirName
        self.dirResults = self.dirAll+'/'+self.opt['timeStamp']
        self.fileFigure = self.dirResults+'/'+self.opt['fileName']

        # setup child objects
        self.norms = apy.plot.norms()
        self.subplot = [apy.plot.subplot(self,row,col) for row in range(nRows) for col in range(nCols)]
        self.nSubplot = len(self.subplot)

        apy.shell.printc('Reading data for %d subplots and %d figures'%(self.nSubplot,self.nFigs))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        True

    # enforce norm values
    def setNorm(self,normID,**kwargs):
        for k,v in kwargs.items():
            self.norms.norms[normID][k] = v

    # select subplot by row and col
    def getSubplot(self, row=0, col=0, **opt):
        if row>=self.nRows:
            apy.shell.exit('Cannot plot row %d out of %d'%(row+1,self.nRows))
        if col>=self.nCols:
            apy.shell.exit('Cannot plot column %d out of %d'%(col+1,self.nCols))
        i = row*self.nCols+col
        if opt: self.subplot[i].setOption(**opt)
        self.subplot[i].canvas['empty'] = False
        return self.subplot[i]
        
    # plot all figures and save the corresponding files
    def plot(self):
        # Plot figures
        pb = apy.util.pb(vmax=self.nFigs,label="Plotting figures")

        #results = apy.util.parallelPool(plotFigure,range(self.nFigs),nproc=8)
        canvas = [sp.getCanvas() for sp in self.subplot]
        optFig = {
            'nRows':      self.nRows,
            'nCols':      self.nCols,
            'nFigs':      self.nFigs,
            'figSize':    (self.nCols*self.opt['sCol'], self.nRows*self.opt['sRow']),
            'fileName':   self.fileFigure+'%03d.'+self.opt['fileFormat'],
            'dirResults': self.dirResults,
            'gridspec':   self.opt['gridspec'],
        }
        arguments = [[f,optFig,canvas] for f in range(self.nFigs)]
        if self.opt['nProc']>1:
            apy.util.parallelPool(plotFigure,arguments,pbar=pb,nproc=self.opt['nProc'])
        else:
            for args in arguments:
                plotFigure(*args)
                pb.increase()
            
        pb.close()
        apy.shell.printc('Figures saved as: %s'%(self.fileFigure+'*.'+self.opt['fileFormat']))
        #self.timer.show()

    def movie(self):
        apy.util.makeMovie(self.fileFigure+'.mp4',self.fileFigure+'*.'+self.opt['fileFormat'])
        apy.shell.printc('Movie saved as: %s.mp4'%self.fileFigure)

    # display all figures
    def show(self,last=False):
        if last:
            if self.opt['debug']:
                dirName = 'debug'
            else:
                dirs = [name for name in os.listdir(self.dirAll) if name not in ['debug','cache']]
                first = np.argsort([int(name.replace("_","")) for name in dirs])[-1]
                dirName = dirs[first]
            fileName = self.dirAll+'/'+dirName+'/'+'*.'+self.opt['fileFormat']
        else:
            fileName = self.fileFigure+'*.'+self.opt['fileFormat']
        apy.util.displayImage(fileName=fileName)


