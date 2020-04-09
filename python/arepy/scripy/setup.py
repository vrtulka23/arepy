import arepy as apy
from subprocess import call
import os

class setup:
    """Simulation setup
    """

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        return

    def __init__(self, proj, *args, **opt):
        self.proj = proj     # project

        # parse arguments
        if proj.sets:
            self.simID = map(int,args[:2])    # simulation ID in the project
            sid = '%03d'%int(args[0])
            self.optSet = self.proj.sets[sid]['opt']
            args = args[2:]
        else:
            self.simID = int(args[0])    # simulation ID in the project
            args = args[1:]

        if args:    
            #self.simPart = str(args[0])  # specifies the part of the setup
            #args = args[1:]
            self.simPart = [str(a) for a in args]
        else: self.simPart = [None]

        self.args = args                 # save the rest of the arguments

        # additional settings
        self.sim = proj.getSimulation(self.simID) # instance of the simulation class
        self.dirSim = proj.dirSim                 # directory with project simulations
        self.dirSetup = proj.dirProject +'/setups/'+ proj.getSetting(self.simID,'setup')  # setup directory 
        self.opt = opt                            # additional options from settings
        self.units = proj.getUnits(self.simID)    # initial units of the simulation
        self.job = proj.getJob(self.simID)        # initial job settings of the simulation
        self.init()                               # custom update of additional options

        # Prepare and copy simulation parts
        apy.shell.printc('Initializing')
        if any(i in [None,'dir'] for i in self.simPart):
            apy.shell.printc('- directory')
            self.setupDirectory()
        if any(i in [None,'config'] for i in self.simPart):
            status = self.setupConfig(self.sim.fileConfig,{})
            if status is not False: apy.shell.printc('- configuration file: '+self.sim.fileConfig)
        if any(i in [None,'param'] for i in self.simPart):
            status = self.setupParam(self.sim.fileParam,{
                'UnitMass_in_g':            self.units['mass'],
                'UnitLength_in_cm':         self.units['length'],
                'UnitVelocity_in_cm_per_s': self.units['velocity'],
            })
            if status is not False: apy.shell.printc('- parameter file: '+self.sim.fileParam)
        if any(i in [None,'run'] for i in self.simPart):
            status = self.setupRun(self.sim.fileRunsh,{
                "NUM_NODES":      self.job['nodes']        if 'nodes'        in self.job else 1,
                "NUM_PROC":       self.job['proc']         if 'proc'         in self.job else 40,
                "JOB_WALL_TIME":  self.job['time']         if 'time'         in self.job else "1:00:00",
                "JOB_TYPE":       self.job['type']         if 'type'         in self.job else "fat",
                "FLAGS_RUN":      self.job['frun']         if 'frun'         in self.job else "",
                "FLAGS_RESTART":  self.job['frestart']     if 'frestart'     in self.job else "1",

                'IMAGE_NODES':    self.job['img_nodes']    if 'img_nodes'    in self.job else 1,
                'IMAGE_PROC':     self.job['img_proc']     if 'img_proc'     in self.job else 40,
                'IMAGE_WALLTIME': self.job['img_walltime'] if 'img_walltime' in self.job else "1:00:00",
                'IMAGE_TYPE':     self.job['img_type']     if 'img_type'     in self.job else "fat",
                'IMAGE_FLAGS':    self.job['img_flags']    if 'img_flags'    in self.job else (0,100,0,1,0,1,0,1),
            })
            if status is not False: apy.shell.printc('- run file'+self.sim.fileRunsh)

        # Do initialization for Arepo simulation with a parameter file
        if apy.shell.isfile(self.sim.fileParam):

            # Prepare and copy simulation parts that depend on the parameter file
            if any(i in [None,'ics','sources','olist'] for i in self.simPart):
                self.sim._initParamNames()        
            if any(i in [None,'ics'] for i in self.simPart):
                apy.shell.printc('- initial conditions: '+self.sim.fileIcs)
                self.setupIcs(self.sim.fileIcs)
            if any(i in [None,'sources'] for i in self.simPart) and hasattr(self.sim,'fileSources'):
                apy.shell.printc('- sources: '+self.sim.fileSources)
                self.setupSources(self.sim.fileSources)
            if any(i in [None,'olist'] for i in self.simPart) and hasattr(self.sim,'fileOlist'):
                apy.shell.printc('- output list: '+self.sim.fileOlist)
                self.setupOlist(self.sim.fileOlist)

            # Create an output directory
            if any(i in [None,'output'] for i in self.simPart):
                if os.path.isdir(self.sim.dirOutput):
                    call(['rm','-f','-r',self.sim.dirOutput])
                if not os.path.isdir(self.sim.dirOutput):
                    call(['mkdir','-p',self.sim.dirOutput])
                if self.sim.linkOutput: # If output directory is external create a symlink
                    if not os.path.islink(self.sim.linkOutput):
                        call(['ln','-s',self.sim.dirOutput,self.sim.linkOutput])

        # Do some other initialization
        if any(i in [None,'other'] for i in self.simPart):
            apy.shell.printc('- other files')
            self.setupOther()

    def init(self):
        """Simulation initialization
        """
        return

    def setupDirectory(self):
        """Dictionary setup
        """
        if os.path.isdir(self.sim.dirSim):
            apy.shell.prompt('Simulation directory already exists, override?')
            call(['rm','-f','-r',self.sim.dirSim])
        if not os.path.isdir(self.sim.dirSim):
            call(['mkdir','-p',self.sim.dirSim])

    def setupConfig(self,fileName,defValues):
        """Configuration file setup
        
        :param str fileName: Path to a configuration file
        :param dict defValues: Default configuration
        """
        return False

    def setupParam(self,fileName,defValues):
        """Parameter file setup
        
        :param str fileName: Path to a parameter file
        :param dict defValues: Default parameters
        """
        return False

    def setupRun(self,fileName,defValues):
        """Run script setup
        
        :param str fileName: Path to a run script file
        :param dict defValues: Default run parameters
        """
        return False
    
    def setupSources(self,fileName):
        """Setup of radiation sources
        
        :param str fileName: Path to a file with sources
        """
        return

    def setupIcs(self,fileName):
        """Setup of initial conditions
        
        :param str fileName: Path to an initial conditions
        """
        return

    def setupOlist(self,fileName):
        """Setup of time output list
        
        :param str fileName: Path to an output list file
        """
        return

    def setupOther(self):
        """Aditional setup"""
        return

    # Create initial output directory
    '''
    def outputIni(self,fileName):
        if not os.path.isdir(self.sim.dirOutputIni):
            call(['mkdir','-p',self.sim.dirOutputIni])
        for f in fileName:
            call(['cp',f,self.sim.dirOutputIni])
    '''
