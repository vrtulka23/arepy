import arepy as apy
import numpy as np

class plot:
    def __init__(self,action,proj,dirName,fileName=None,*args):
        self.proj = proj                      # project object
        self.args = args                      # additional arguments
        self.timeStamp = apy.util.timeStamp() # time stamp for all plots
        self.opt = {}                         # global plot options
        self.optPlot = None                   # plot options

        if action=='debug':                   # set debugging mode
            self.debug = True
            action = 'plot'
        else:
            self.debug = False

        self.dirName = dirName                                     # name of the plot directory
        self.fileName = dirName if fileName is None else fileName  # name of the plot file
        self.dirPlot = self.dirName+'/'+self.fileName              # path to the file directory

        self.nproc = {
            'fig': 1,                         # number of processors to use for figures
            'kdt': 1,                         # number of processors to use for KDTree
            'snap': 1,                        # number of processors to use for snapshot
        }

        self.fig = None
        self.tab = None
        self.grps = None

        self.init()                           # initialization of the plot        

        if action=='plot':
            self._plot()
        elif action=='show':
            self._show()
        elif action=='movie':
            self._movie()
            
    def init(self):
        return

    def getSimulation(self,sim,**opt):
        if 'initSnap' in opt:
            if isinstance(opt['initSnap'],dict) and 'nproc' not in opt['initSnap']:
                opt['initSnap']['nproc'] = self.nproc['snap']
            else:
                opt['initSnap'] = {'nproc': self.nproc['snap']}
        return self.proj.getSimulation(sim,**opt)

    # Set number of available processors
    def setProcessors(self,fig=1,kdt=1,snap=1):
        self.nproc = {
            'fig':  fig,
            'kdt':  kdt,
            'snap': snap
        }

    # Add group
    def setGroups(self,names,options,**opt):
        nopt = {
            'dirCache': self.proj.dirResults+'/'+self.dirPlot+'/cache',
            'nproc':    self.nproc['fig'],
            'n_jobs':   self.nproc['kdt']
        }
        nopt.update(opt)
        self.grps = apy.files.collection(names=names,options=options,**nopt)

    # Add a new figure to the list of plots
    def setFigure(self,ncol,nrow,nfig,movie=False,show=False,debug=False,plot=True,**opt):
        nopt = {
            'debug':      np.any([debug,self.debug]),
            'fileName':   self.fileName,
            'dirName':    self.dirPlot,
            'dirResults': self.proj.dirResults,
            'timeStamp':  self.timeStamp,
            'nproc':      self.nproc['fig'],
        }
        nopt.update(opt)
        self.optPlot = {
            'type':'figure',
            'ncol':ncol,
            'nrow':nrow,
            'nfig':nfig,
            'movie':movie,
            'show':show,
            'plot':plot,
            'opt':nopt,
        }

    # Add new table to the list of plots
    def setTable(self,show=False,debug=False,**opt):
        nopt = {
            'debug':      np.any([debug,self.debug]),
            'fileName':   self.fileName,
            'dirName':    self.dirPlot,
            'dirResults': self.proj.dirResults,
        }
        nopt.update(opt)
        self.optPlot = {
            'type':'table',
            'show':show,
            'opt':nopt,
        }

    # plot
    def plot(self):
        return
    def _plot(self):
        if self.optPlot is None:
            apy.shell.exit("Plot '%s' was not set (plot.py)"%(self.dirPlot))
        if self.optPlot['type']=='figure':
            self.fig = apy.plot.figure(self.optPlot['ncol'],self.optPlot['nrow'],self.optPlot['nfig'],**self.optPlot['opt'])
            self.plot()
            if self.optPlot['plot']:
                self.fig.plot()
            if self.optPlot['show']:
                self.fig.show()
            if self.optPlot['movie']:
                self.fig.movie()
        elif self.optPlot['type']=='table':
            self.tab = apy.data.table(**self.optPlot['opt'])
            self.plot()
            self.tab.save()
            if self.optPlot['show']:
                self.tab.show()
                    
    # display
    def _show(self):
        if self.optPlot is None:
            apy.shell.exit("Plot '%s' was not set (plot.py)"%(self.dirPlot))
        if self.optPlot['type']=='figure':
            self.fig = apy.plot.figure(self.optPlot['ncol'],self.optPlot['nrow'],self.optPlot['nfig'],**self.optPlot['opt'])
            self.fig.show(last=True)
        elif self.optPlot['type']=='table':
            self.tab = apy.data.table(**self.optPlot['opt'])
            with open(self.tab.fileName, 'r') as f:
                contents = f.read()
                print(contents)

    # movie
    def _movie(self):
        if self.optPlot is None:
            apy.shell.exit("Plot '%s' was not set (plot.py)"%(self.dirPlot))
        if self.optPlot['type']=='figure':
            self.fig = apy.plot.figure(self.optPlot['ncol'],self.optPlot['nrow'],self.optPlot['nfig'],**self.optPlot['opt'])
            self.fig.movie()
        elif self.optPlot['type']=='table':
            apy.shell.exit('Cannot plot movie from a table (plot.py)')
