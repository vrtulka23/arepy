import arepy as apy
import numpy as np
import os

class project:
    """Project class

    :var str dirSim: Absolute path to the simulation directory
    :var dict sims: Set of basic simulation settings

    .. note::
        
        The simulation directory path has to be always specified. It is used
        by the bash script in the run.sh file to check whether the current directory
        belongs to some project.
    """
    
    def __init__(self,name):
        self.name = name
        self.dirProject = apy.dirScripy+'/'+name
        self.dirResults = apy.dirResults+'/'+name
        self.dirTemplates = apy.dirArepy+'/scripy/tmpl' 
        
        self.config = apy.shell.readConfigFile(self.dirProject + "/project.conf")
        self.dirSim = self.config["dirSim"]
        self.dirPlots = self.dirProject+'/plots'
        self.dirScripts = self.dirProject+'/scripts'
        self.dirSetups = self.dirProject+'/setups'
        self.sims = {}
        self.sets = {}
        self.opt = {}
        self.init()
        
        # Set a default simulation directory if not specified otherwise
        for key,val in self.sims.items():
            if 'dir' not in val:
                self.sims[key]['dir'] = self.dirSim

    # Custom initialization
    def init(self):
        """Initial settings of a project

        This method should be overloaded by any derived project classes
        and it should consist following two settings:

        1) A path to the simulation data.
        2) Basic settings of the simulations
        
        A minimalistic setting will look like::

            # Simulation directory of a project
            self.dirSim = "/simulation/directory"
    
            # Setup of a new simulation
            self.sims['001'] = {
                'dir': self.dirSim+'/subdirectory',
                'name':'first',
                'setup':'first',
                'job':{'nodes':1,'proc':40,'time':'1:00:00','type':'fat'},
                'units':{'length':apy.const.pc,'time':apy.const.yr},
                'opt':{}
            }
        """
        self.dirSim = None
        self.sims['001'] ={'name':'default','setup':'default'}

    # Additional functions
    def getUnits(self, simID):
        """Get units of a simulation
        
        :param int simID: Simulation ID
        :return: Units
        :rtype: :class:`arepy.units`
        """
        simSet, simID = [None,int(simID)] if np.isscalar(simID) else map(int,simID)
        settings = self.sims['%03d'%simID]
        units = apy.units( settings['units'] ) if 'units' in settings else None        
        return units

    def getJob(self, simID):
        """Get job settings of a simulation

        :param int simID: Simulation ID
        :return dict: A dictionary with job settings
        """
        simSet, simID = [None,int(simID)] if np.isscalar(simID) else map(int,simID)
        settings = self.sims['%03d'%simID]
        job = settings['job'] if 'job' in settings else None        
        return job

    def getSimulation(self, simID, **nopt):
        """Get simulation object

        :param int simID: Simulation ID
        :param dict nopt: Simulation options
        :return: Simulation object
        :rtype: :class:`arepy.files.simulation`
        """
        simSet, simID = [None,int(simID)] if np.isscalar(simID) else map(int,simID)
        settings = self.sims['%03d'%simID]
        if simSet is None:
            dirSet = settings['dir']
        else:
            dirSet = self.sets['%03d'%simSet]['dir']
        dirSim = dirSet+'/%03d_%s'%(simID,settings['name'])
        opt = {'initChem':'sgchem1'}
        if 'sim' in settings:
            opt.update(settings['sim'])
        opt.update(nopt)
        return apy.files.simulation( dirSim, name=settings['name'], sid=simID, **opt)

    def getSetting(self,simID,name):
        """Get simulation settings

        :param int simID: Simulation ID
        :param str name: Name of the setting
        :return dict: Simulation settings
        """
        simSet, simID = [None,int(simID)] if np.isscalar(simID) else map(int,simID)
        settings = self.sims['%03d'%simID]
        if simSet is not None:
            settings['optSet'] = self.sets['%03d'%simSet]['opt']
        return settings[name]

    #################################
    # BASH functions
    #################################

    def initProj(self,name):
        """Initialization of a new scripy project

        :param str name: Name of the project in a format: [a-zA-Z0-9]+

        This method can be triggered via command line:

        .. code:: bash
            
            apy --init-project myproject
        """
        self.dirProject = apy.dirScripy+'/'+name
        apy.shell.mkdir( self.dirProject )
        dirProjectInit = self.dirProject+'/__init__.py'
        dirProjectConf = self.dirProject+'/project.conf'
        with apy.util.template( self.dirTemplates+'/project.py' ) as f:
            f.write( dirProjectInit )
        with apy.util.template( self.dirTemplates+'/project.conf' ) as f:
            f.write( dirProjectConf )
        apy.shell.printc('New project:\n'+self.dirProject+'\n'+dirProjectInit)

    def initSetup(self,name):
        """Initialization of a new scripy setup

        :param str name: Name of the setup in a format: [a-zA-Z0-9]+

        This method can be triggered via command line:

        .. code:: bash
            
            apy --init-setup mysetup
        """
        if not apy.shell.isdir( self.dirSetups ):
            apy.shell.mkdir( self.dirSetups )
            apy.shell.touch( self.dirSetups+'/__init__.py' )
        dirSetup = self.dirSetups+'/%s'%name
        dirSetupInit = dirSetup+'/__init__.py'
        with apy.util.template( self.dirTemplates+'/setup.py' ) as f:
            apy.shell.mkdir( dirSetup )
            f.write( dirSetupInit )            
        apy.shell.printc('New setup:\n'+dirSetup+'\n'+dirSetupInit)
            
    def initPlot(self,name):
        """Initialization of a new scripy plot

        :param str name: Name of the plot in a format: [a-zA-Z0-9]+

        This method can be triggered via command line:

        .. code:: bash
            
            apy --init-plot myplot
        """
        if not apy.shell.isdir( self.dirPlots ):
            apy.shell.mkdir( self.dirPlots )
            apy.shell.touch( self.dirPlots+'/__init__.py' )
        with apy.util.template( self.dirTemplates+'/plot.py' ) as f:
            dirPlot = self.dirPlots+'/%s'%name
            apy.shell.mkdir( dirPlot )
            f.replace('nameProject',self.name)
            f.replace('namePlot',name)
            f.write( dirPlot+'/__init__.py' )

    def initScript(self,name):
        """Initialization of a new scripy script

        :param str name: Name of the script in a format: [a-zA-Z0-9]+

        This method can be triggered via command line:

        .. code:: bash
            
            apy --init-script myscript
        """
        if not apy.shell.isdir( self.dirScripts ):
            apy.shell.mkdir( self.dirScripts )
            apy.shell.touch( self.dirScripts+'/__init__.py' )
        with apy.util.template( self.dirTemplates+'/script.py' ) as f:
            f.write( self.dirScripts+'/%s.py'%name )

    # List all available plots
    def _showOptions(self,dirName):
        for f in os.listdir(dirName):
            if f.endswith(".py") and f!='__init__.py':
                print( '%-20s'%f.replace('.py',''), )
        print( '' )
            
    # Setup simulation 
    # apy --setup {SIM_ID} [{PART}]
    def setup(self, *args):
        simSet,simID = (int(args[0]),int(args[1])) if self.sets else (None, int(args[0]))
        settings = self.sims['%03d'%simID]
        opt = settings['opt'] if 'opt' in settings else {}
        exec("from scripy.%s.setups.%s import *"%(self.name,settings['setup']),globals())
        if 'type' in settings and settings['type'] is not None:
            name = 'setup_%s'%settings['type']
            globals()[name](self,*args,**opt)
        else:
            setup(self,*args,**opt)

    # Analyze and plot simulation data
    # apy (--plot|--debug|--show) {PLOT} [{SUBPLOT}]
    def plot(self,action,name=None,*args):
        print(name)
        if name is None:
            self._showOptions(self.dirPlots)
        else: 
            apy.shell.printc("Plot '%s' for project '%s'"%(str(name),self.name))
            #exec("from scripy.%s.plots.%s import *"%(self.name,str(name)),globals())
            self.timer = apy.util.timer()
            name = str(name)
            if args:
                nameClass = "scripy.%s.plots.%s.%s"%(self.name,name,args[0])
                exec("from %s import *"%nameClass,globals())
                fn = str(args[0])
                if fn in globals():
                    globals()[fn](action,self,name,args[0],*args[1:])
                else:
                    apy.shell.exit("Class '%s' was not found in '%s'! (project.py)"%(fn,nameClass))
            else:
                exec("from scripy.%s.plots.%s import *"%(self.name,name),globals())
                globals()[name](action,self,name,name,*args)
            self.timer.end()

    # Run a script
    # apy --script {NAME}
    def script(self,name=None,*args):
        if name is None:
            self._showOptions(self.dirScripts)
        else: 
            apy.shell.printc("Script '%s' for project '%s'"%(str(name),self.name))
            exec("from scripy.%s.scripts.%s import *"%(self.name,str(name)),globals())
            self.timer = apy.util.timer()
            script(self,*args)
            self.timer.end()
            
