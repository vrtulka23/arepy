import os
from subprocess import call
import arepy as apy

''' Example use:

class setup(scr.setup):
    def init(self):
        self.opt['MeshRelax'] = True
    def config(self,fileName):
        f = apy.files.config(self.dirSetup+'/Config.sh')
        f.setValue({
             'MESHRELAX': self.opt['MeshRelax']
        })
        f.write(fileName)
    ...
'''

class setup:
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
            self.simPart = str(args[0])  # specifies the part of the setup
            args = args[1:]
        else: self.simPart = None
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
        if self.simPart in [None,'dir']:
            self.setupDirectory()
        if self.simPart in [None,'config']:
            self.setupConfig(self.sim.fileConfig,{})
        if self.simPart in [None,'param']:
            self.setupParam(self.sim.fileParam,{
                'UnitMass_in_g':            self.units['mass'],
                'UnitLength_in_cm':         self.units['length'],
                'UnitVelocity_in_cm_per_s': self.units['velocity'],
            })
        if self.simPart in [None,'run']:
            self.setupRun(self.sim.fileRunsh,{
                "NUM_NODES":     self.job['nodes'] if 'nodes'       in self.job else 1,
                "NUM_PROC":      self.job['proc']  if 'proc'        in self.job else 40,
                "JOB_WALL_TIME": self.job['time']  if 'time'        in self.job else "1:00:00",
                "JOB_TYPE":      self.job['type']  if 'type'        in self.job else "fat",
                "FLAGS_RUN":     self.job['frun']  if 'frun'        in self.job else "",
                "FLAGS_RESTART": self.job['frestart'] if 'frestart' in self.job else "1",

                'IMAGE_NODES':    self.job['img_nodes']    if 'img_nodes'    in self.job else 1,
                'IMAGE_PROC':     self.job['img_proc']     if 'img_proc'     in self.job else 40,
                'IMAGE_WALLTIME': self.job['img_walltime'] if 'img_walltime' in self.job else "1:00:00",
                'IMAGE_TYPE':     self.job['img_type']     if 'img_type'     in self.job else "fat",
                'IMAGE_FLAGS':    self.job['img_flags']    if 'img_flags'    in self.job else (0,100,0,1,0,1,0,1),
            })

        # Prepare and copy simulation parts that depend on the parameter file
        if self.simPart in [None,'ics','sources','olist']:
            self.sim.initParamNames()        
        if self.simPart in [None,'ics']:
            self.setupIcs(self.sim.fileIcs)
        if self.simPart in [None,'sources'] and hasattr(self.sim,'fileSources'):
            self.setupSources(self.sim.fileSources)
        if self.simPart in [None,'olist'] and hasattr(self.sim,'fileOlist'):
            self.setupOlist(self.sim.fileOlist)

        # Create an output directory
        if self.simPart in [None,'output']:
            if os.path.isdir(self.sim.dirOutput):
                call(['rm','-f','-r',self.sim.dirOutput])
            if not os.path.isdir(self.sim.dirOutput):
                call(['mkdir','-p',self.sim.dirOutput])
            if self.sim.linkOutput: # If output directory is external create a symlink
                if not os.path.islink(self.sim.linkOutput):
                    call(['ln','-s',self.sim.dirOutput,self.sim.linkOutput])

        # Do some other initialization
        if self.simPart in [None,'other']:
            self.setupOther()

    # additional initialization
    def init(self):
        return

    # Create the main simulation directory
    def setupDirectory(self):
        if os.path.isdir(self.sim.dirSim):
            apy.shell.prompt('Simulation directory already exists, override?')
            call(['rm','-f','-r',self.sim.dirSim])
        if not os.path.isdir(self.sim.dirSim):
            call(['mkdir','-p',self.sim.dirSim])

    # Create a configuration file
    def setupConfig(self,fileName):
        return

    # Create a parameter file
    def setupParam(self,fileName):
        return

    # Create a running scrip
    def setupRun(self,fileName):
        return
    
    # Create a file with sources
    def setupSources(self,fileName):
        return

    # Create initial conditions
    def setupIcs(self,fileName):
        return

    # Create an list of output times
    def setupOlist(self,fileName):
        return

    # Do some additional initialization
    def setupOther(self):
        return

    # Create initial output directory
    '''
    def outputIni(self,fileName):
        if not os.path.isdir(self.sim.dirOutputIni):
            call(['mkdir','-p',self.sim.dirOutputIni])
        for f in fileName:
            call(['cp',f,self.sim.dirOutputIni])
    '''
