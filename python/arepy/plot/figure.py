import numpy as np
import arepy as apy
from arepy.plot.plot import *
import os

class figure:
    """Figure class

    :param int nrows: Number of subplot rows
    :param int ncols: Number of subplot columns
    :param int nfigs: Number of figures

    :param str fileFormat: Format of the output file (png/pdf)
    """

    def __init__(self, nrows=1, ncols=1, nfigs=1, **opt):
        
        # initial settings
        self.nrows = int(nrows)     # number of subplots in the row
        self.ncols = int(ncols)     # number of subplots in the column
        self.nfigs = int(nfigs)     # number of figures to plot
        
        # set options
        self.opt = {
            'debug':      False,
            'dirResults': 'results',
            'dirName':    None,
            'fileName':   'figOverview', 
            'timeStamp':  apy.util.timeStamp(),
            'srow':       3.0, 
            'scol':       3.5,
            'nproc':      1,
            'gridspec':   None,                  # use GridSpec axes
            'axesgrid':   None,                  # use AxesGrid
            'imagegrid':  None,                  # use ImageGrid
            'fileFormat': 'png',                 # file format of the final figure (png,pdf,jpeg,...)
            'projection': None,                  # default value of projection for each subplot
        }
        self.opt.update(opt)

        if self.opt['nproc']>self.nfigs:
            self.opt['nproc'] = self.nfigs

        if self.opt['debug']: # use debug time stamp
            apy.shell.printc('Debugging mode is on!!!','r')            
            self.opt['timeStamp'] = 'debug'

        dirName = self.opt['fileName'] if self.opt['dirName'] is None else self.opt['dirName']
        self.dirAll = self.opt['dirResults']+'/'+dirName            # group directory
        self.dirResults = self.dirAll+'/'+self.opt['timeStamp']     # plot directory
        self.fileFigure = self.dirResults+'/'+self.opt['fileName']  # complete figure path

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
    def setSubplot(self, row=0, col=0, xyz=False, **opt):
        """Set subplot options
        
        :param int row: Row of the subplot
        :param int col: Column of the subplot
        """
        i = self.getIndex(row,col)
        self.subplot[i].setOption(**opt)        
        if xyz:
            self.subplot[i].xyz = True
            self.subplot[i].canvas['subplot'][3] = True

    def getSubplot(self, row=0, col=0, xyz=False, **opt):
        """Get subplot
        
        :param int row: Row of the subplot
        :param int col: Column of the subplot
        :return: Subplot object
        :rkey: :class:`arepy.plot.subplot`
        """
        i = self.getIndex(row,col)
        if opt or xyz: self.setSubplot(row,col,xyz,**opt)
        self.subplot[i].canvas['empty'] = False
        return self.subplot[i]

    def getIndex(self, row=0, col=0):
        if row>=self.nrows:
            apy.shell.exit('Cannot plot row %d out of %d (figure.py)'%(row+1,self.nrows))
        if col>=self.ncols:
            apy.shell.exit('Cannot plot column %d out of %d (figure.py)'%(col+1,self.ncols))
        return row*self.ncols+col
        
    # plot all figures and save the corresponding files
    def plot(self):

        # clean the debug directory
        if self.opt['debug']: 
            if apy.shell.isdir(self.dirResults):
                apy.shell.rm(self.dirResults)
            apy.shell.mkdir(self.dirResults)
        
        # Plot figures
        pb = apy.shell.pb(vmax=self.nfigs,label="Plotting figures")

        canvas = [sp.getCanvas() for sp in self.subplot]
        optFig = {
            'nrows':      self.nrows,
            'ncols':      self.ncols,
            'nfigs':      self.nfigs,
            'figSize':    (self.ncols*self.opt['scol'], self.nrows*self.opt['srow']),
            'fileName':   self.fileFigure+'%03d.'+self.opt['fileFormat'],
            'dirResults': self.dirResults,
            'gridspec':   self.opt['gridspec'],
            'axesgrid':   self.opt['axesgrid'],
            'imagegrid':  self.opt['imagegrid'],
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
        apy.shell.displayImage(fileName=fileName)


