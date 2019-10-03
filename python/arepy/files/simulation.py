import numpy as np
import arepy as apy
import os, glob, re
from subprocess import call

#
# Example:
# sim = apy.files.simulation("./")
# snap = sim.getSnapshot(236)
# data = snap.getProperty("Masses")
#
class simulation:
    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        return

    def __init__(self, dirSim='.', name='', **opt):
        # update default options
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
            **opt
        }

        # set initial parameters
        self.dirSim = dirSim
        self.name = name

        if 'nproc' not in self.opt:
            self.opt['nproc'] = self.opt['nsub']

        # set names of files and directories
        self.dirCache = self.dirSim+'/cache'
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
            apy.shell.printc('         '+self.fileConfig,'r')
            cf = None
        if apy.shell.isfile(self.fileParam): 
            pf = apy.files.param(self.fileParam) 
        else:
            apy.shell.printc('Warning: Parameter file does not exist','r')
            apy.shell.printc('         '+self.fileParam,'r')
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
                self.dirOutputIni = self.opt['dirOutput']+'_ini'
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
            if cf.getValue('SGCHEM'):
                if cf.getValue('CHEMISTRYNETWORK')==1:
                    self.optChem = {'type':'sgchem1'}
            else:
                apy.shell.exit('Chemistry has to be initialized (simulation.py)')

        if self.optChem['type']=='sgchem1':
            self.optChem['rates'] = [ 'RIH', 'HRIH', 'RIH2', 'HRIH2', 'RDH2', 'HRD', 'RIHE', 'HRIHE' ]
            self.optChem['images'] = [ 'rih', 'xHP' ]
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
        if opt is not False:
            names = ['NumFilesPerSnapshot','ComovingIntegrationOn']
            values = pf.getValue(names)
            self.optSnap = {
                'nsub':values[0],
                'nproc':values[0],
                'initChem':self.optChem,
                'comoving':True if values[1] else False,
            }
            if isinstance(opt,dict):
                self.optSnap.update(opt)
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
    def dirSnap(self,snap,init=False):
        dirName = self.dirOutputIni if init else self.dirOutput
        if self.opt['nsub']>1: 
            snapNum = '%03d'%snap if isinstance(snap,(int,float)) else snap
            dirName = dirName+'/'+self.dirNameSnap%snapNum      
        return dirName

    # Compose a sink file name
    def fileSink(self,snap=None):
        if snap is None:
            fileSink = self.dirSnap('*') if self.opt['nsub']>1 else self.fileNameSink%'*'
        else:
            snapNum = '%03d'%snap
            fileSink = self.fileNameSink%(snapNum) if self.opt['nsub']>1 else self.fileNameSink%snapNum
        return self.dirSnap(snap) +'/'+ fileSink        

    # Compose a snapshot file name
    def fileSnap(self,snap=None,init=False):
        if snap is None:
            fileSnap = self.dirSnap('*') if self.opt['nsub']>1 else self.fileNameSnap%'*'
        else:
            snapNum = '%03d'%snap
            fileSnap = self.fileNameSnap%(snapNum+'.%d') if self.opt['nsub']>1 else self.fileNameSnap%snapNum
        return self.dirSnap(snap,init) +'/'+ fileSnap

    ######################
    # Get simulation files
    ######################
    
    def getImage(self, isnap, iprop, itype):
        if iprop in self.optChem['rates']:
            i = self.optChem['rates'].index(iprop)
            fileImage = self.fileImage%('sxrates',itype,isnap)
            return apy.files.image( fileImage, len(self.optChem['rates']), i )            
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
        if self.optSinks is not None:
            nopt['sinkOpt']  = self.optSinks.copy()
            nopt['sinkOpt']['fileName'] = self.fileSink(snap)
        return apy.files.snap(fileName,**nopt)

    def getSink(self,snap,**opt):
        nopt = self.optSinks.copy()
        nopt.update(opt)
        nopt['fileName'] = self.fileSink(snap)
        return apy.files.sink(**nopt)        
        
    def getSources(self):
        return apy.files.sources(self.fileSources)

    def getParameters(self):
        return apy.files.param(self.fileParam)

    def getConfig(self):
        return apy.files.config(self.fileConfig)

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

    # find snapshot number at given times  DEPRECATED: too slow!!
    '''
    def findSnapsAtTimes(self,times,**opt):
        snaps = self.getSnapNums()
        snapTimes = np.zeros(len(snaps))
        for s,snap in enumerate(snaps):
            with self.getSnapshot(snap,**opt) as sf:
                snapTimes[s] = sf.getHeader('Time')
                print(s,snap,snapTimes[s])
        return np.round(np.interp(times,snapTimes,snaps)).astype(int)
    '''

    def hasSnapshot(self,snap):
        return apy.shell.isfile(self.fileSnap(snap))

    # Get snapshot numbers of 'times'
    def getSnapAtTimes(self,times):
        csn = self.cacheSnapNums()
        return np.round(np.interp(times,csn['Time'],csn['Snapshot'])).astype(int)

    # Get snapshot numbers of 'times' after the formation of a first sink particle
    def getSnapAfterFirstSink(self,times):
        csn = self.cacheSnapNums()
        nsinks = csn['NumPart_Total'][:,5]
        if np.any(nsinks>0): # substract a formation time of the first sink particle
            sink = self.getSink(csn['Snapshot'][-1])
            csn['Time'] -= np.min(sink.getValues('FormationTime'))
        else:                # use normal times instead
            apy.shell.printc("Warning: There are no sink particles in the simulation '%s'! (simulation.py)"%self.name,"r")
        return np.round(np.interp(times,csn['Time'],csn['Snapshot'])).astype(int)        

    ##############################################
    # Cache header or data values for each snapshot
    ##############################################
    
    def cacheSnapNums(self):
        snaps = self.getSnapNums()
        grp = apy.files.group(self, snaps, dirCache=self.dirCache, nproc=apy.numCpu)
        return grp.foreach(cacheSnapNums,cache=self.name,update=True)

# Cache snapshot times
def cacheSnapNums(item):
    snap = item.getSnapshot()
    header = snap.getHeader(['Time','NumPart_Total'])
    return {
        'Snapshot':      item.snap,
        'Time':          header['Time'],
        'NumPart_Total': header['NumPart_Total'],
    }
