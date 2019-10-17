import arepy as apy
import numpy as np

class plot:
    """General class of a plot
    
    :var arepy.files.collection grps: Groups object
    :var arepy.plot.figure fig: Figure object
    :var arepy.data.table tab: Table object

    .. note::
        
        Note that class variables 'grps', 'fig' and 'tab' are accessible only in the 'plot()' function
    """
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

        self.settings()                       # plot settings
        self.init()                           # initialization of the plot        

        if action=='plot':
            self._plot()
        elif action=='show':
            self._show()
        elif action=='movie':
            self._movie()

    def settings(self):
        """Plot settings

        This is the place for general settings of the simulation.
        In principle, data set in this functions should be available for all subplots.
        For example the plotting units can be set here::
        
            self.opt['simOpt'] = {
                'initUnitsNew': {'length':apy.const.pc},
                'initImages':True,
                'initSinks':True,
                'initSnap': True,
            }
        """
        return
            
    def init(self):
        """Initialization of a plot

        This is the place for particular settings of the plot.
        A basic figure setup could be::
        
            # allocate processors
            self.setProcessors( fig=6 )
        
            # setup snapshot groups
            self.setGroups(['names','sim','snaps'],[            
                ('nrpm3',4, [100,33]),
                ('nrp0', 5, [65,23]),
            ])
        
            # setup figure
            self.setFigure(2,1,2)
        """
        return

    # plot
    def plot(self):
        """Main plotting routine

        This method prepares the figure for plotting.
        A simple plotting routine could look like::
            
            # loop through all groups
            for grp in self.grps:
        
                # setup a simulation
                sim = self.getSimulation(grp.opt['sim'],**self.opt['simOpt'])

                # add snapshot to the group
                grp.addSnapshot(sim,grp.opt['snaps'])
        
                # select a subplot where we plot data
                sp = self.fig.getSubplot(grp.index,0, xlabel='x',ylabel='y' )
        
                # plot an image
                grp.setImage(sp,'density','slice')
        """
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

    def getSimulation(self,sim,**opt):
        """Get a project simulation
        
        :param int sim: Simulation ID
        :param dict opt: Additional simulation settings
        """
        if 'initSnap' in opt:
            if isinstance(opt['initSnap'],dict) and 'nproc' not in opt['initSnap']:
                opt['initSnap']['nproc'] = self.nproc['snap']
            else:
                opt['initSnap'] = {'nproc': self.nproc['snap']}
        return self.proj.getSimulation(sim,**opt)

    def setProcessors(self,fig=1,kdt=1,snap=1):
        """Distribute number of processors
        
        :param int fig: Number of processors used for figure plotting
        :param int kdt: Number of processors used by a KDTree algorithm
        :param int snap: Number of processors used to read a multi-file snapshot
        
        Example::
            
            self.setProcessors( fig=apy.numCpu )
        """
        self.nproc = {
            'fig':  fig,
            'kdt':  kdt,
            'snap': snap
        }

    def setGroups(self,names,options,**opt):
        """Set simulation groups
        
        :param list[str] names: Table column names
        :param list[tuple] options: Table rows
        :param dict opt: Additional group options

        This function sets to the class a variable
        
            self.grps

        that contains all the group information.
        
        Example::
            
            self.setGroups(['names','sim','snaps'],[
                ( 'hydroHelium', 18, 30 ),
                ( 'hydroOnly',   21, 30 ),
            ])
        """
        nopt = {
            'dirCache': self.proj.dirResults+'/'+self.dirPlot+'/cache',
            'nproc':    self.nproc['fig'],
            'n_jobs':   self.nproc['kdt']
        }
        nopt.update(opt)
        self.grps = apy.files.collection(names=names,options=options,**nopt)

    def setFigure(self,ncol,nrow,nfig,movie=False,show=False,debug=False,plot=True,**opt):
        """Set a new figure
        
        :param int ncol: Number of collumns
        :param int nrow: Number of rows
        :param int nfig: Number of figures
        :param float srow: Size of the subplot rows on the figure (figsize)
        :param float scol: Size of the subplot cols on the figure (figsize)
        :param bool movie: Create a movie from all figures
        :param bool show: Display figures at the end of the plotting
        :param bool debug: Save figures into a debug folder
        :param bool plot: Plot figures
        :param dict gridspec: Gridspec options
        :param dict tickparam: Parameters of the axis ticks and their labels
        :param list[str] group: List of grouped axis elements in case of several subplots

        Example::
            
            self.setFigure(2,1,1,show=True,scol=4,srow=2, gridspec={'hspace':0.1}, group=['xlabel'],
                           tickparam={'axis':'both','direction':'in','top':True,'right':True})
        """
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
            'plot':plot,
            'movie':movie if plot else False,
            'show':show if plot else False,
            'opt':nopt,
        }

    def setTable(self,show=False,debug=False,**opt):
        """Set a new table

        :param bool show: Display table at the end of the calculation
        :param bool debug: Save table into a debug folder
        :param dict opt: Additional table options
        """
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
