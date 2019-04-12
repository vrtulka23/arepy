import arepy as apy

class plot:
    def __init__(self,action,proj,dirName,fileName=None,*args):
        self.proj = proj                      # project object
        self.args = args                      # additional arguments
        self.timeStamp = apy.util.timeStamp() # time stamp for all plots
        self.opt = {}                         # global plot options
        self.optPlot = None                   # plot options

        self.dirName = dirName                                     # name of the plot directory
        self.fileName = dirName if fileName is None else fileName  # name of the plot file
        self.dirPlot = self.dirName+'/'+self.fileName              # path to the file directory

        self.nproc = 1                        # number of available processors

        self.fig = None
        self.tab = None
        self.grps = None

        self.init()                           # initialization of the plot        

        if action=='plot':
            self._plot()
        elif action=='show':
            self._show()
            
    def init(self):
        return

    # Set number of available processors
    def setProcessors(self,nproc):
        self.nproc = nproc

    # Add group
    def setGroups(self,names,options,**opt):
        nopt = {
            'dirCache': self.proj.dirResults+'/'+self.dirPlot+'/cache',
            'nproc':    self.nproc,
        }
        nopt.update(opt)
        self.grps = apy.files.groups(names=names,options=options,**nopt)

    # Add a new figure to the list of plots
    def setFigure(self,ncol,nrow,nfig,movie=False,show=False,debug=False,**opt):
        nopt = {
            'debug':      debug,
            'fileName':   self.fileName,
            'dirName':    self.dirPlot,
            'dirResults': self.proj.dirResults,
            'timeStamp':  self.timeStamp,
            'nproc':      self.nproc,
        }
        nopt.update(opt)
        self.optPlot = {
            'type':'figure',
            'ncol':ncol,
            'nrow':nrow,
            'nfig':nfig,
            'movie':movie,
            'show':show,
            'opt':nopt,
        }

    # Add new table to the list of plots
    def setTable(self,show=False,debug=False,**opt):
        nopt = {
            'debug':      debug,
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
