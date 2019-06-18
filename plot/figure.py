import numpy as np
import arepy as apy
from arepy.plot.plot import *
import os

class figure:

    def __init__(self, nrows=1, ncols=1, nfigs=1, **opt):
        
        # initial settings
        self.nrows = nrows     # number of subplots in the row
        self.ncols = ncols     # number of subplots in the column
        self.nfigs = nfigs     # number of figures to plot
        
        # set options
        self.opt = {
            'debug':      False,
            'dirResults': 'results',
            'dirName':    None,
            'fileName':   'figOverview', 
            'timeStamp':  apy.util.timeStamp(),
            'sRow':       3.0, 
            'sCol':       3.5,
            'nproc':      1,
            'gridspec':   None,                  # use GridSpec axes
            'axesgrid':   None,                  # use AxesGrid
            'fileFormat': 'png',                 # file format of the final figure (png,pdf,jpeg,...)
            'projection': None,                  # default value of projection for each subplot
        }
        self.opt.update(opt)

        if self.opt['nproc']>self.nfigs:
            self.opt['nproc'] = self.nfigs

        if self.opt['debug']:
            apy.shell.printc('Debugging mode is on!!!','r')
            self.opt['timeStamp'] = 'debug'

        dirName = self.opt['fileName'] if self.opt['dirName'] is None else self.opt['dirName']
        self.dirAll = self.opt['dirResults']+'/'+dirName
        self.dirResults = self.dirAll+'/'+self.opt['timeStamp']
        self.fileFigure = self.dirResults+'/'+self.opt['fileName']

        # setup child objects
        self.norms = apy.plot.norms()
        self.subplot = [apy.plot.subplot(self,row,col) for row in range(nrows) for col in range(ncols)]
        self.nSubplot = len(self.subplot)

        apy.shell.printc('Reading data for %d subplots and %d figures'%(self.nSubplot,self.nfigs))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        True

    # enforce norm values
    def setNorm(self,normID,**kwargs):
        for k,v in kwargs.items():
            self.norms.norms[normID][k] = v

    # select subplot by row and col
    def getIndex(self, row=0, col=0):
        if row>=self.nrows:
            apy.shell.exit('Cannot plot row %d out of %d (figure.py)'%(row+1,self.nrows))
        if col>=self.ncols:
            apy.shell.exit('Cannot plot column %d out of %d (figure.py)'%(col+1,self.ncols))
        return row*self.ncols+col
    def setSubplot(self, row=0, col=0, **opt):
        i = self.getIndex(row,col)
        self.subplot[i].setOption(**opt)        
    def getSubplot(self, row=0, col=0, **opt):
        i = self.getIndex(row,col)
        if opt: self.setSubplot(row,col,**opt)
        self.subplot[i].canvas['empty'] = False
        return self.subplot[i]
        
    # plot all figures and save the corresponding files
    def plot(self):
        # Plot figures
        pb = apy.shell.pb(vmax=self.nfigs,label="Plotting figures")

        canvas = [sp.getCanvas() for sp in self.subplot]
        optFig = {
            'nrows':      self.nrows,
            'ncols':      self.ncols,
            'nfigs':      self.nfigs,
            'figSize':    (self.ncols*self.opt['sCol'], self.nrows*self.opt['sRow']),
            'fileName':   self.fileFigure+'%03d.'+self.opt['fileFormat'],
            'dirResults': self.dirResults,
            'gridspec':   self.opt['gridspec'],
            'axesgrid':   self.opt['axesgrid'],
        }
        arguments = [[f,optFig,canvas] for f in range(self.nfigs)]
        if self.opt['nproc']>1:
            apy.util.parallelPool(plotFigure,arguments,pbar=pb,nproc=self.opt['nproc'])
        else:
            for args in arguments:
                plotFigure(*args)
                pb.increase()
            
        pb.close()
        apy.shell.printc('Figures saved as: %s'%(self.fileFigure+'*.'+self.opt['fileFormat']))

    def movie(self):
        apy.shell.makeMovie(self.fileFigure+'.mp4',self.fileFigure+'*.'+self.opt['fileFormat'])
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


