import numpy as np
import arepy as apy
import os, glob, re
from subprocess import call

class simulation:
    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        return

    def __init__(self, dirSim='.', name='', **opt):

        # set initial parameters
        self.dirSim = dirSim
        self.name = name
        self.opt = {
            'fileNameParam': 'param.txt',
            'fileNameConfig': 'Config.sh',
            'fileNameIcs': 'ics.hdf5',
            'comoving': False,
            'nsub':  1,
            'dirResults': 'results',
            'initChem': False,     # initialize chemistry settings
            'initUnitsNew': False, # loads new units
            'initUnitsOld': False, # loads old units
            'initUnits': False,    # loads units
            'initSnap': False,     # loads snap settings
            'initSinks': False,    # loads sink settings from the config file
            'initImages': False,   # loads image settings from the parameter file
            # other: nproc, dirOutput
        }
        self.opt.update(opt)
        if 'nproc' not in self.opt:
            self.opt['nproc'] = self.opt['nsub']

        # set names of files and directories
        self.dirSimIcs = self.dirSim+'/ics'
        self.fileParam = self.dirSim+'/'+self.opt['fileNameParam']
        self.fileConfig = self.dirSim+'/'+self.opt['fileNameConfig']
        self.fileIcs = self.dirSimIcs+'/'+self.opt['fileNameIcs']
        self.fileRunsh = self.dirSim +'/run.sh'
        if self.opt['dirResults'][0]=='/':
            self.dirResults = self.opt['dirResults']
        else:
            self.dirResults = self.dirSim+'/'+self.opt['dirResults']
        if apy.shell.isfile(self.fileParam):
            self.initParamNames()
            
        if apy.shell.isfile(self.fileConfig):
            cf = apy.files.config(self.fileConfig) 
        else:
            apy.shell.printc('Warning: Configuration file does not exist','r')
            cf = None
        if apy.shell.isfile(self.fileParam): 
            pf = apy.files.param(self.fileParam) 
        else:
            apy.shell.printc('Warning: Parameter file does not exist','r')
            pf = None

        if self.opt['initUnitsNew']:
            self.opt['initUnits'] = {'new':self.opt['initUnitsNew']}
        if self.opt['initUnitsOld']:
            self.opt['initUnits'] = {'old':self.opt['initUnitsOld']}

        self.initChem(cf,pf,self.opt['initChem'])     # initialize chemistry properties
        self.initUnits(cf,pf,self.opt['initUnits'])   # initialize units from the parameter file
        self.initSnap(cf,pf,self.opt['initSnap'])     # initialize sink file settings
        self.initSinks(cf,pf,self.opt['initSinks'])   # initialize sink file settings
        self.initImages(cf,pf,self.opt['initImages']) # initialize sink file settings

    ###########################
    # Additional initialization
    ###########################

    # Initialize additional file/dir names dependant on the parameter file
    def initParamNames(self):
        with apy.files.param(self.fileParam) as f:
            params = ['InitCondFile','OutputDir','SnapshotFileBase','TestSrcFile','OutputListOn','OutputListFilename']
            fIcs, dOutput, fSnapBase, fSources, isOlist, fOlist = f.getValue(params)
            if 'dirOutput' in self.opt:
                self.dirOutput = self.opt['dirOutput']
                self.linkOutput = self.dirSim +'/output'
            elif dOutput[0]=='/':
                self.dirOutput = dOutput
                self.linkOutput = self.dirSim +'/output'
            else:
                self.dirOutput = self.dirSim +'/'+ dOutput
                self.linkOutput = None
            self.dirOutputIni = self.dirSim +'/'+ dOutput + '_ini'
            self.dirNameSnap = fSnapBase + 'dir_%s'
            self.fileNameSnap = fSnapBase + '_%s.hdf5'
            self.fileNameSink = 'sink_'+fSnapBase+'_%s'
            self.fileImage = self.dirOutput + '/%s_%s_%03d'
            self.fileIcs = self.dirSim +'/'+ fIcs +'.hdf5'
            if fSources is not None:
                self.fileSources = fSources if fSources[0]=='/' else self.dirSim +'/'+ fSources
            if isOlist==1:
                self.fileOlist = fOlist if fOlist[0]=='/' else self.dirSim +'/'+ fOlist

    # Initialize constants
    def initChem(self,cf,pf,opt):
        if isinstance(opt,dict):
            self.optChem = opt.copy()
        elif isinstance(opt,str):
            self.optChem = {'type':opt}
        else:
            apy.shell.exit('Chemistry has to be initialized (simulation.py)')
        if self.optChem['type']=='sgchem1':
            if 'abund' not in self.optChem:
                if cf and cf.getValue('SX_HYDROGEN_ONLY'):
                    self.optChem['abund'] = 'HydrogenOnly'

    # Initialize units
    def initUnits(self,cf,pf,opt):
        def loadOld():
            names = ['UnitMass_in_g','UnitLength_in_cm','UnitVelocity_in_cm_per_s','UnitPhotons_per_s']
            values = pf.getValue(names)
            return {'mass':values[0],'length':values[1],'velocity':values[2],'flux':values[3]}
        if opt is True:
            self.units = apy.units(old=loadOld())
        elif isinstance(opt,dict):
            old = opt['old'] if 'old' in opt else loadOld()
            new = opt['new'] if 'new' in opt else None
            self.units = apy.units(old=old,new=new)
        else:
            self.units = None

    # Initialize snapshot file settings
    def initSnap(self,cf,pf,opt):
        if opt is True:
            names = ['NumFilesPerSnapshot','ComovingIntegrationOn']
            values = pf.getValue(names)
            self.optSnap = {
                'nsub':values[0],
                'nproc':values[0],
                'initChem':self.optChem,
                'comoving':True if values[1] else False,
            }
        else:
            dopt = {'nsub':1, 'nproc':1, 'initChem':self.optChem, 'comoving':False}
            self.optSnap = dopt.update(opt) if isinstance(opt,dict) else dopt

    # Initialize sink file settings
    def initSinks(self,cf,pf,opt):
        if opt is True:
            values = cf.getValue(['SINK_SIMPLEX','SINK_PARTICLES_VARIABLE_ACC_RADIUS',
                                  'SGCHEM_ACCRETION_LUMINOSITY','SINK_PARTICLES_FEEDBACK'])
            self.optSinks = {'simplex':values[0],'varAccRad':values[1],'accLum':values[2],'sinkFeed':values[3]}
        else:
            self.optSinks = opt if isinstance(opt,dict) else {}

    # Initialize image file settings
    def initImages(self,cf,pf,opt):
        if opt is True:
            self.optImages = {
                'boxSize':np.array( pf.getValue(['PicXmin','PicXmax','PicYmin','PicYmax','PicZmin','PicZmax']) ),
                'pixels':np.array( pf.getValue(['PicXpixels','PicYpixels']) )
            }
        else:
            self.optImages = opt if isinstance(opt,dict) else {}
                
    #####################################
    # Routines that create file/dir names
    #####################################

    # Compose a snapshot directory name
    def dirSnap(self,snap):
        if self.opt['nsub']>1: 
            snapNum = '%03d'%snap if isinstance(snap,(int,float)) else snap
            return self.dirOutput+'/'+self.dirNameSnap%snapNum      
        else:
            return self.dirOutput

    # Compose a sink file name
    def fileSink(self,snap=None):
        if snap is None:
            fileSink = self.dirSnap('*') if self.opt['nsub']>1 else self.fileNameSink%'*'
        else:
            snapNum = '%03d'%snap
            fileSink = self.fileNameSink%(snapNum) if self.opt['nsub']>1 else self.fileNameSink%snapNum
        return self.dirSnap(snap) +'/'+ fileSink        

    # Compose a snapshot file name
    def fileSnap(self,snap=None):
        if snap is None:
            fileSnap = self.dirSnap('*') if self.opt['nsub']>1 else self.fileNameSnap%'*'
        else:
            snapNum = '%03d'%snap
            fileSnap = self.fileNameSnap%(snapNum+'.%d') if self.opt['nsub']>1 else self.fileNameSnap%snapNum
        return self.dirSnap(snap) +'/'+ fileSnap

    ######################
    # Get simulation files
    ######################
    
    def getImage(self, isnap, iprop, itype):
        imageTypes = getattr(apy.files,self.optChem['type']).const.imageTypes
        if iprop in imageTypes:
            i = imageTypes.index(iprop)
            fileImage = self.fileImage%('sxrates',itype,isnap)
            return apy.files.image( fileImage, len(imageTypes), i )            
        elif iprop=='ndens':
            fileImage = self.fileImage%('density',itype,isnap)
            im,px,py = apy.files.image( fileImage )            
            im *= self.units['density']
            im /= apy.const.m_p if self.optChem['abund']=='HydrogenOnly' else 1.22*apy.const.m_p
            return im,px,py
        elif isinstance(iprop,dict):
            if iprop['name']=='Normed': # Example: {'name':'Normed','p':'ndens','n':1e3}
                im,px,py = self.getImage(isnap,iprop['p'],itype)
                im /= iprop['n']
                return im,px,py
        else:
            fileImage = self.fileImage%(iprop,itype,isnap)
            return apy.files.image( fileImage )

    def getSnapshot(self,snap,**opt):
        fileName = self.fileSnap(snap)
        nopt = self.optSnap.copy()
        nopt.update(opt)
        return apy.files.snap(fileName,**nopt)

    def getSink(self,snap,**opt):
        fileName = self.fileSink(snap)
        nopt = self.optSinks.copy()
        nopt.update(opt)
        return apy.files.sink(fileName,**nopt)        
        
    def getSources(self):
        return apy.files.sources(self.fileSources)

    def getParameters(self):
        return apy.files.param(self.fileParam)

    #############################################
    # Get additional information about simulation
    #############################################
            
    def getSnapNums(self):
        snapFiles = glob.glob(self.fileSnap())
        snapNums = np.zeros(len(snapFiles),dtype=int)
        for s,snap in enumerate(snapFiles):
            snap = os.path.basename(snap)
            pattern = self.fileNameSnap%"([0-9]+)"
            m = re.match(pattern, snap)
            snapNums[s] = m.group(1)
        return np.sort(snapNums)

    def hasSnapshot(self,snap):
        return apy.shell.isfile(self.fileSnap(snap))

    # DEBUG: Deprecated... use scripy setup!!!
    def setup(self,fileConfig=None,fileParam=None,fileRunsh=None,fileIni=[],fileOther=[],symLinks=None):

        # Create a new simulation dir, delete the previous if exists
        if os.path.isdir(self.dirSim):
            apy.shell.prompt('Simulation directory already exists, override?')
            call(['rm','-f','-r',self.dirSim])
        if not os.path.isdir(self.dirSim):
            call(['mkdir','-p',self.dirSim])

        # Create Config.sh file
        if fileConfig is not None:
            if isinstance(fileConfig,str):
                call(['cp',fileConfig,self.fileConfig])
            else:
                fileConfig.write( self.fileConfig )
                
        # Create param.txt file
        if fileParam is not None:
            if isinstance(fileParam,str):
                call(['cp',fileParam,self.fileParam])
            else:
                fileParam.write( self.fileParam )

        # Create run.sh file
        if fileRunsh is not None:
            if isinstance(fileRunsh,str):
                call(['cp',fileRunsh,self.fileRunsh])
            else:
                fileRunsh.write( self.fileRunsh )
            call(['chmod','+x',self.fileRunsh])

        # Create rest of the paths
        self.initParamNames()        

        # Create an output directory
        if os.path.isdir(self.dirOutput):
            call(['rm','-f','-r',self.dirOutput])
        if not os.path.isdir(self.dirOutput):
            call(['mkdir','-p',self.dirOutput])
        if self.linkOutput: # If output directory is external create a symlink
            if not os.path.islink(self.linkOutput):
                call(['ln','-s',self.dirOutput,self.linkOutput])            

        if fileIni:
            if not os.path.isdir(self.dirOutputIni):
                call(['mkdir','-p',self.dirOutputIni])
            for f in fileIni:
                call(['cp',f,self.dirOutputIni])
            
        # Create other directories
        if not os.path.isdir(self.dirResults):
            call(['mkdir','-p',self.dirResults])

        # Copy other files to the directory
        for f in fileOther:
            call(['cp',f,self.dirSim])

        # Create symbolic links
        if symLinks is not None:
            for link,target in symLinks.items():
                if not os.path.islink(link):
                    call(['ln','-s',target,link])
