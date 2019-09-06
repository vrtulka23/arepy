import arepy as apy
import numpy as np
import os

class project:
    def __init__(self,name):
        self.name = name
        self.dirProject = apy.dirScripy+'/'+name
        self.dirResults = apy.dirResults+'/'+name
        self.dirTemplates = apy.dirArepy+'/scripy/tmpl' 
        
        self.dirPlots = self.dirProject+'/plots'
        self.dirScripts = self.dirProject+'/scripts'
        self.dirSetups = self.dirProject+'/setups'
        self.sims = {}
        self.sets = {}
        self.opt = {}
        self.init()

    # Custom initialization
    def init(self):
        self.sims['001'] ={'name':'default','setup':'default'}

    # Additional functions
    def getUnits(self, simID):
        simSet, simID = [None,int(simID)] if np.isscalar(simID) else map(int,simID)
        settings = self.sims['%03d'%simID]
        units = apy.units( settings['units'] ) if 'units' in settings else None        
        return units

    def getJob(self, simID):
        simSet, simID = [None,int(simID)] if np.isscalar(simID) else map(int,simID)
        settings = self.sims['%03d'%simID]
        job = settings['job'] if 'job' in settings else None        
        return job

    def getSimulation(self, simID, **nopt):
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
        return apy.files.simulation( dirSim, name=settings['name'], **opt)

    def getSetting(self,simID,name):
        simSet, simID = [None,int(simID)] if np.isscalar(simID) else map(int,simID)
        settings = self.sims['%03d'%simID]
        if simSet is not None:
            settings['optSet'] = self.sets['%03d'%simSet]['opt']
        return settings[name]

    #################################
    # BASH functions
    #################################

    # Create a new project 
    # apy --init-project {NAME}
    def initProj(self,name,dirData):
        self.dirProject = apy.dirScripy+'/'+name
        apy.shell.mkdir( self.dirProject )
        apy.shell.mkdir( dirData )
        with open(apy.dirModule+'/settings/projects.txt','w+') as f:
            f.write(name+'='+dirData+'\n')
        with apy.util.template( self.dirTemplates+'/project.py' ) as f:
            f.write( self.dirProject+'/__init__.py' )
        apy.shell.printc('New project: '+self.dirProject)
            
    # Create a new plot 
    # apy --init-plot {NAME}
    def initPlot(self,name):
        if not apy.shell.isdir( self.dirPlots ):
            apy.shell.mkdir( self.dirPlots )
            apy.shell.touch( self.dirPlots+'/__init__.py' )
        with apy.util.template( self.dirTemplates+'/plot.py' ) as f:
            dirPlot = self.dirPlots+'/%s'%name
            apy.shell.mkdir( dirPlot )
            f.replace('nameProject',self.name)
            f.replace('namePlot',name)
            f.write( dirPlot+'/__init__.py' )

    # Create a new setup
    # apy --init-setup {NAME}
    def initSetup(self,name):
        if not apy.shell.isdir( self.dirSetups ):
            apy.shell.mkdir( self.dirSetups )
            apy.shell.touch( self.dirSetups+'/__init__.py' )
        with apy.util.template( self.dirTemplates+'/setup.py' ) as f:
            dirSetup = self.dirSetups+'/%s'%name
            apy.shell.mkdir( dirSetup )
            f.write( dirSetup+'/__init__.py' )            

    # Create a new script 
    # apy --init-script {NAME}
    def initScript(self,name):
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
            
