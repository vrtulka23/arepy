import re
import arepy as apy
import numpy as np

class param():
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        True
    
    def __init__(self,fileName=None,show=False,notes=False):
        self.groups = [
            {'id':1,  'name':'Relevant files',
             'params':['InitCondFile','OutputDir','SnapshotFileBase']},
            {'id':2,  'name':'File formats',
             'params':['ICFormat','SnapFormat']},
            {'id':3,  'name':'CPU-time limits',
             'params':['TimeLimitCPU','CpuTimeBetRestartFile','ResubmitCommand',
                       'ResubmitOn','CoolingOn','StarformationOn']},
            {'id':4,  'name':'Memory allocation',
             'params':['MaxMemSize']},
            {'id':5,  'name':'Charactertics of the run / type & accuracy of time integration',
             'params':['PeriodicBoundariesOn', 'ComovingIntegrationOn', 'TimeBegin', 'TimeMax', 
                       'TypeOfTimestepCriterion', 'ErrTolIntAccuracy', 'CourantFac', 'MaxSizeTimestep', 'MinSizeTimestep']},
            {'id':6,  'name':'Output frequency and output paramaters',
             'params':['OutputListOn', 'OutputListFilename', 'TimeOfFirstSnapshot', 'TimeBetSnapshot', 'TimeBetStatistics', 
                       'NumFilesPerSnapshot', 'NumFilesWrittenInParallel']},
            {'id':7,  'name':'Cosmological parameters',
             'params':['Omega0', 'OmegaLambda', 'OmegaBaryon', 'HubbleParam', 'BoxSize']},
            {'id':8,  'name':'System of units',
             'params':['UnitLength_in_cm', 'UnitMass_in_g', 'UnitVelocity_in_cm_per_s', 'GravityConstantInternal']},
            {'id':9,  'name':'Treatment of empty space and temperature limits',
             'params':['InitGasTemp', 'MinEgySpec', 'MinGasTemp', 'MinimumDensityOnStartUp', 'LimitUBelowThisDensity', 
                       'LimitUBelowCertainDensityToThisValue']},
            {'id':10, 'name':'Tree algorithm, force accuracy, domain update frequency',
             'params':['TypeOfOpeningCriterion', 'ErrTolTheta', 'ErrTolForceAcc']},
            {'id':11, 'name':'Computational efficiency parameter',
             'params':['MultipleDomains', 'TopNodeFactor', 'ActivePartFracForNewDomainDecomp']},
            {'id':12, 'name':'SPH PARMETERS / Initial density estimate',
             'params':['DesNumNgb', 'MaxNumNgbDeviation', 'MinVolume', 'MaxVolume', 'MaxVolumeDiff']},
            {'id':13, 'name':'Gravitational softening lengths',
             'params':['GasSoftFactor']},
            {'id':14, 'name':'Adaptive hydro softening parameters',
             'params':['MinimumComovingHydroSoftening', 'AdaptiveHydroSofteningSpacing']},
            {'id':15, 'name':'Plummer-equivalent gravitational softening length [code units]',
             'params':['SofteningComovingType0', 'SofteningComovingType1', 'SofteningComovingType2', 'SofteningComovingType3', 
                       'SofteningComovingType4', 'SofteningComovingType5']},
            {'id':16, 'name':'If Comoving integration switched on, then this is the physical softening length',
             'params':['SofteningMaxPhysType0', 'SofteningMaxPhysType1', 'SofteningMaxPhysType2', 'SofteningMaxPhysType3', 
                       'SofteningMaxPhysType4', 'SofteningMaxPhysType5']},
            {'id':17, 'name':'Assignment of particular softening lengths to arepo particle types',
             'params':['SofteningTypeOfPartType0', 'SofteningTypeOfPartType1', 'SofteningTypeOfPartType2', 
                       'SofteningTypeOfPartType3', 'SofteningTypeOfPartType4', 'SofteningTypeOfPartType5']},
            {'id':18, 'name':'Mesh regularisation & refinement',
             'params':['CellMaxAngleFactor', 'CellShapingSpeed', 'ReferenceGasPartMass', 'TargetGasMassFactor', 
                       'RefinementCriterion', 'DerefinementCriterion']},
            {'id':19, 'name':'SGChem - chemistry options (Clark et al 2011 ApJ)',
             'params':['SGChemInitH2Abund', 'SGChemInitHPAbund', 'SGChemInitDIIAbund', 'SGChemInitHDAbund', 
                       'SGChemInitHeIIIAbund']},
            {'id':20, 'name':'SGChem - for networks 5 & 13',
             'params':['SGChemInitCPAbund', 'SGChemInitCOAbund']},
            {'id':21, 'name':'SGChem - for Nelson and Langer 99',
             'params':['SGChemInitCHxAbund', 'SGChemInitOHxAbund', 'SGChemInitHCOPAbund', 'SGChemInitHePAbund', 
                       'SGChemInitMPAbund']},
            {'id':22, 'name':'SGChem - elemental abundances',
             'params':['CarbAbund', 'OxyAbund', 'MAbund', 'ZAtom', 'AtomicCoolOption', 'DeutAbund', 'H2OpacityOption']},
            {'id':23, 'name':'SGChem - dust properties',
             'params':['InitDustTemp', 'UVFieldStrength', 'DustToGasRatio', 'CosmicRayIonRate', 'InitRedshift', 
                       'ExternalDustExtinction']},
            {'id':24, 'name':'SGChem - strenght of H2 formation heating',
             'params':['H2FormEx', 'H2FormKin']},
            {'id':25, 'name':'Photochemistry',
             'params':['PhotoApprox', 'ISRFOption','SGChemConstInitAbundances', 'LWBGType', 'LWBGStartRedsh']},
            {'id':26, 'name':'Sink particles',
             'params':['SinkCreationDensityCodeUnits', 'SinkFormationRadius', 'SinkEvolutionDumpRateYears', 
                       'SGChemAccretionLuminosityOn', 'SinkAccretionRateSmoothingMass']},
            {'id':27, 'name':'MHD',
             'params':['MHDSeedDir', 'MHDSeedValue']},
            {'id':28, 'name':'Slice Image',
             'params':['PicXpixels', 'PicYpixels', 'PicXaxis', 'PicYaxis', 'PicZaxis', 
                       'PicXmin', 'PicXmax', 'PicYmin', 'PicYmax', 'PicZmin', 'PicZmax']},
            {'id':29, 'name':'SimpleX radiation transport',
             'params':['UnitPhotons_per_s','MinNumPhotons','TestSrcFile']},
            {'id':30, 'name':'Other','params':[]}
        ]
        self.params = {
            'InitCondFile': {'dtype':'s','default':'ics.hdf5','format':'%s'},
            'OutputDir': {'dtype':'s','default':'output','format':'%s'},
            'SnapshotFileBase': {'dtype':'s','default':'snap_','format':'%s'},
            
            'ICFormat': {'dtype':'i','default':3,'format':'%d'},
            'SnapFormat': {'dtype':'i','default':3,'format':'%d'},
            
            'TimeLimitCPU': {'dtype':'i','default':0,'format':'%d'},
            'CpuTimeBetRestartFile': {'dtype':'f','default':0,'format':'%.1f'},
            'ResubmitCommand': {'dtype':'s','default':'/path/to/submit/script','format':'%s'},
            'ResubmitOn': {'dtype':'i','default':0,'format':'%d'},
            'CoolingOn': {'dtype':'i','default':0,'format':'%d'},
            'StarformationOn': {'dtype':'i','default':0,'format':'%d'},
            
            'MaxMemSize': {'dtype':'f','default':0,'format':'%.1f'},
            
            'PeriodicBoundariesOn': {'dtype':'i','default':0,'format':'%d'},
            'ComovingIntegrationOn': {'dtype':'i','default':0,'format':'%d'},
            'TimeBegin': {'dtype':'f','default':0,'format':'%.4f'},
            'TimeMax': {'dtype':'f','default':0,'format':'%.4f'},
            'TypeOfTimestepCriterion': {'dtype':'i','default':0,'format':'%d'},
            'ErrTolIntAccuracy': {'dtype':'f','default':0,'format':'%f'},
            'CourantFac': {'dtype':'f','default':0,'format':'%f'},
            'MaxSizeTimestep': {'dtype':'f','default':0,'format':'%.3e'},
            'MinSizeTimestep': {'dtype':'f','default':0,'format':'%.3e'},
            
            'Omega0': {'dtype':'f','default':0,'format':'%f'},
            'OmegaLambda': {'dtype':'f','default':0,'format':'%f'},
            'OmegaBaryon': {'dtype':'f','default':0,'format':'%f'},
            'HubbleParam': {'dtype':'f','default':0,'format':'%f'},
            'BoxSize': {'dtype':'f','default':0,'format':'%f'},
            
            'UnitLength_in_cm': {'dtype':'f','default':0,'format':'%e','note':'cm'},
            'UnitMass_in_g': {'dtype':'f','default':0,'format':'%e','note':'g'},
            'UnitVelocity_in_cm_per_s': {'dtype':'f','default':0,'format':'%e','note':'cm/s'},
            'GravityConstantInternal': {'dtype':'i','default':0,'format':'%d'},
            
            'InitGasTemp': {'dtype':'f','default':0,'format':'%f'},
            'MinEgySpec': {'dtype':'f','default':0,'format':'%f'},
            'MinGasTemp': {'dtype':'f','default':0,'format':'%f'},
            'MinimumDensityOnStartUp': {'dtype':'f','default':0,'format':'%f'},
            'LimitUBelowThisDensity': {'dtype':'i','default':0,'format':'%d'},
            'LimitUBelowCertainDensityToThisValue': {'dtype':'i','default':0,'format':'%d'},
            
            'OutputListOn': {'dtype':'i','default':0,'format':'%d'},
            'OutputListFilename': {'dtype':'s','default':'output_list','format':'%s'},
            'TimeBetSnapshot': {'dtype':'f','default':0,'format':'%.2e'},
            'TimeOfFirstSnapshot': {'dtype':'f','default':0,'format':'%.2e'},
            'TimeBetStatistics': {'dtype':'f','default':0,'format':'%.2e'},
            'NumFilesPerSnapshot': {'dtype':'i','default':1,'format':'%d'},
            'NumFilesWrittenInParallel': {'dtype':'i','default':1,'format':'%d'},
            
            'TypeOfOpeningCriterion': {'dtype':'i','default':1,'format':'%d'},
            'ErrTolTheta': {'dtype':'f','default':0.7,'format':'%f'},
            'ErrTolForceAcc': {'dtype':'f','default':0.0025,'format':'%f'},
            
            'MultipleDomains': {'dtype':'i','default':8,'format':'%d'},
            'TopNodeFactor': {'dtype':'i','default':5,'format':'%d'},
            'ActivePartFracForNewDomainDecomp': {'dtype':'f','default':0,'format':'%f'},
            
            'DesNumNgb': {'dtype':'i','default':32,'format':'%d'},
            'MaxNumNgbDeviation': {'dtype':'i','default':1,'format':'%d'},
            'MinVolume': {'dtype':'f','default':0,'format':'%e'},
            'MaxVolume': {'dtype':'f','default':1e6,'format':'%e'},
            'MaxVolumeDiff': {'dtype':'i','default':6,'format':'%d'},
            
            'GasSoftFactor': {'dtype':'f','default':1.5,'format':'%.2f'},
            
            'MinimumComovingHydroSoftening': {'dtype':'f','default':0,'format':'%e'},
            'AdaptiveHydroSofteningSpacing': {'dtype':'f','default':0,'format':'%f'},
            
            'SofteningComovingType0': {'dtype':'f','default':0,'format':'%e'},
            'SofteningComovingType1': {'dtype':'f','default':0,'format':'%e'},
            'SofteningComovingType2': {'dtype':'f','default':0,'format':'%e'},
            'SofteningComovingType3': {'dtype':'f','default':0,'format':'%e'},
            'SofteningComovingType4': {'dtype':'f','default':0,'format':'%e'},
            'SofteningComovingType5': {'dtype':'f','default':0,'format':'%e'},
            
            'SofteningMaxPhysType0': {'dtype':'f','default':0,'format':'%e'},
            'SofteningMaxPhysType1': {'dtype':'f','default':0,'format':'%e'},
            'SofteningMaxPhysType2': {'dtype':'f','default':0,'format':'%e'},
            'SofteningMaxPhysType3': {'dtype':'f','default':0,'format':'%e'},
            'SofteningMaxPhysType4': {'dtype':'f','default':0,'format':'%e'},
            'SofteningMaxPhysType5': {'dtype':'f','default':0,'format':'%e'},
            
            'SofteningTypeOfPartType0': {'dtype':'i','default':0,'format':'%d'},
            'SofteningTypeOfPartType1': {'dtype':'i','default':1,'format':'%d'},
            'SofteningTypeOfPartType2': {'dtype':'i','default':2,'format':'%d'},
            'SofteningTypeOfPartType3': {'dtype':'i','default':3,'format':'%d'},
            'SofteningTypeOfPartType4': {'dtype':'i','default':4,'format':'%d'},
            'SofteningTypeOfPartType5': {'dtype':'i','default':5,'format':'%d'},
            
            'CellMaxAngleFactor': {'dtype':'f','default':0,'format':'%f'},
            'CellShapingSpeed': {'dtype':'f','default':0,'format':'%f'},
            'ReferenceGasPartMass': {'dtype':'f','default':0,'format':'%e'},
            'TargetGasMassFactor': {'dtype':'f','default':0,'format':'%f'},
            'RefinementCriterion': {'dtype':'i','default':0,'format':'%d'},
            'DerefinementCriterion': {'dtype':'i','default':0,'format':'%d'},
            
            'SGChemInitH2Abund': {'dtype':'f','default':1e-3,'format':'%.3e'},
            'SGChemInitHPAbund': {'dtype':'f','default':1e-7,'format':'%.3e'},
            'SGChemInitDIIAbund': {'dtype':'f','default':2.6e-12,'format':'%.3e'},
            'SGChemInitHDAbund': {'dtype':'f','default':3e-7,'format':'%.3e'},
            'SGChemInitHeIIIAbund': {'dtype':'f','default':0,'format':'%.3e'},
            'SGChemInitCPAbund': {'dtype':'f','default':0,'format':'%.3e'},
            'SGChemInitCOAbund': {'dtype':'f','default':0,'format':'%.3e'},
            'SGChemInitCHxAbund': {'dtype':'f','default':0,'format':'%.3e'},
            'SGChemInitOHxAbund': {'dtype':'f','default':0,'format':'%.3e'},
            'SGChemInitHCOPAbund': {'dtype':'f','default':0,'format':'%.3e'},
            'SGChemInitHePAbund': {'dtype':'f','default':0,'format':'%.3e'},
            'SGChemInitMPAbund': {'dtype':'f','default':0,'format':'%.3e'},
            'CarbAbund': {'dtype':'f','default':0,'format':'%e'},
            'OxyAbund': {'dtype':'f','default':0,'format':'%e'},
            'MAbund': {'dtype':'f','default':0,'format':'%e'},
            'ZAtom': {'dtype':'f','default':0,'format':'%e'},
            'AtomicCoolOption': {'dtype':'i','default':0,'format':'%d'},
            'DeutAbund': {'dtype':'f','default':2.6e-5,'format':'%e'},
            'H2OpacityOption': {'dtype':'i','default':0,'format':'%d'},
            'InitDustTemp': {'dtype':'f','default':0,'format':'%f'},                 # Kelvin
            'UVFieldStrength': {'dtype':'f','default':0,'format':'%e'},
            'DustToGasRatio': {'dtype':'f','default':0,'format':'%e'},
            'CosmicRayIonRate': {'dtype':'f','default':0,'format':'%e'},
            'InitRedshift': {'dtype':'f','default':0,'format':'%f'},
            'ExternalDustExtinction': {'dtype':'f','default':0,'format':'%f'},
            'H2FormEx': {'dtype':'f','default':0,'format':'%f'},
            'H2FormKin': {'dtype':'f','default':0,'format':'%f'},
            'PhotoApprox': {'dtype':'i','default':0,'format':'%d'},
            'ISRFOption': {'dtype':'i','default':0,'format':'%d'},
            'SGChemConstInitAbundances': {'dtype':'i','default':0,'format':'%d'},
            'LWBGType': {'dtype':'i','default':0,'format':'%d'},
            'LWBGStartRedsh': {'dtype':'i','default':0,'format':'%d'},
            
            'SinkCreationDensityCodeUnits': {'dtype':'f','default':0,'format':'%.4e'},  # code units density
            'SinkFormationRadius': {'dtype':'f','default':0,'format':'%.4e'},           # code units length
            'SinkEvolutionDumpRateYears': {'dtype':'f','default':0,'format':'%.4e'},
            'SGChemAccretionLuminosityOn': {'dtype':'i','default':0,'format':'%d'},
            'SinkAccretionRateSmoothingMass': {'dtype':'f','default':0,'format':'%.4e'},
            
            'MHDSeedDir': {'dtype':'i','default':0,'format':'%d'},
            'MHDSeedValue': {'dtype':'f','default':0,'format':'%.2f'},
            
            'UnitPhotons_per_s': {'dtype':'f','default':1e48,'format':'%.3e','note':'ph/s'},  # ph/s
            'MinNumPhotons': {'dtype':'f','default':1e-5,'format':'%.3e'},
            'TestSrcFile': {'dtype':'s','default':'test_sources.bin','format':'%s'},
            
            'PicXpixels': {'dtype':'i','default':1000,'format':'%d'},
            'PicYpixels': {'dtype':'i','default':1000,'format':'%d'},
            'PicXaxis': {'dtype':'i','default':0,'format':'%d'},
            'PicYaxis': {'dtype':'i','default':1,'format':'%d'},
            'PicZaxis': {'dtype':'i','default':2,'format':'%d'},
            'PicXmin': {'dtype':'f','default':0,'format':'%.5e'},  # code units length
            'PicXmax': {'dtype':'f','default':1,'format':'%.5e'},  # code units length
            'PicYmin': {'dtype':'f','default':0,'format':'%.5e'},  # code units length
            'PicYmax': {'dtype':'f','default':1,'format':'%.5e'},  # code units length
            'PicZmin': {'dtype':'f','default':0,'format':'%.5e'},  # code units length
            'PicZmax': {'dtype':'f','default':1,'format':'%.5e'},  # code units length
        }
        # parameters that need to be set manually
        self.needToSet = []

        if fileName!=None:
            self.read(fileName,show=show,notes=notes)

    def parse(self, rmGroups=[], rmParams=[], cmGroups=[], cmParams=[]):
        output = ''
        for group in self.groups:
            if group['id'] in rmGroups: continue
            gOutput = ''
            for param in group['params']:
                if param in rmParams: continue
                if 'value' in self.params[param]:
                    if (param in cmParams) or (group['name'] in cmGroups):
                        gOutput += "% "
                    gOutput += self._parse(param)
                    gOutput += '\n'
                else:
                    if param in self.needToSet:
                        apy.shell.exit("Parameter \'%s\' need to be set!"%param)
                    
            if gOutput!='':
                output += "%%---- %s\n"%group['name'] + gOutput + "\n";
        return output

    def _parse(self,param):
        output = "%-40s "%(param) 
        output += self.params[param]['format']%self.params[param]['value'] 
        if 'note' in self.params[param]:
            output += '   % '+self.params[param]['note']
        return output

    def read(self,fileName,show=False,notes=False):
        with open(fileName,'r') as f:
            content = f.read()
        lines = content.split("\n")
        for line in lines:
            m = re.match("([\_a-zA-Z0-9]+)\s*(\*\*\*|[\/\_\+\.\-a-zA-Z0-9]+)\s*[\%]*(.*)",line)
            if m==None: continue
            param = m.group(1)
            if m.group(2)=="***":
                self.needToSet.append(param)
            else:
                note = m.group(3) if notes else None
                self.setValue(param,m.group(2),note)

        if show==True:
            print( self.parse() )

    def write(self,fileName,rmGroups=[],rmParams=[],cmGroups=[],cmParams=[],meshrelax=False):
        if meshrelax:
            rmGroups.extend([28])  # remove image settings
        output = self.parse(rmGroups=rmGroups,rmParams=rmParams,cmGroups=cmGroups,cmParams=cmParams)
        for param in self.needToSet:
            print( self._parse(param) )
        with open(fileName,'w') as f:
            f.write(output)

    def _setValue(self,param,value=None,note=None):
        if param in self.params:
            if value is False:
                del self.params[param]['value']
                if param in self.needToSet:
                    self.needToSet.remove(param)
                return
            if value is None:
                value = self.params[param]['default']
            dtype = self.params[param]['dtype']
            if (dtype=='i'):
                value = int(value)
            elif (dtype=='f'):
                value = float(value)
            elif (dtype=='s'):
                value = str(value)
            self.params[param]["value"] = value
        else:
            if value==None: value = ''
            print( apy.shell.textc("Unknown parameter '%s' was moved to the group 'Other'"%param,'red') )
            self.params[param] = {'dtype':'s','default':'','format':'%s','value':str(value)}
            self.groups[-1]['params'].append(param)
        if note!=None and note!='':
            self.params[param]['note'] = note
    def setValue(self,param,value=None,note=None):
        if isinstance(param,dict):
            for p,v in param.items():
                self._setValue(p,v)
        else:
            self._setValue(param,value,note)
    
    def getValue(self,names):
        allNames = [names] if isinstance(names,str) else names
        data = []
        for name in allNames:
            data.append( self.params[name]['value'] if 'value' in self.params[name] else None )
        return data[0] if isinstance(names,str) else data        

    def formatValue(self,param,value=None):
        if value is None:
            value = self.getValue(param)
        return '' if value is None else self.params[param]['format']%value
    
def paramCompare(fname,gname):
    f = apy.files.param(fname)
    g = apy.files.param(gname)
    output = apy.shell.textc('Comparing parameter files\nFile 1: %s\nFile 2: %s\n'%(fname,gname))
    for group in f.groups:
        gOutput = ''
        for param in group['params']:
            if 'value' in f.params[param] or 'value' in g.params[param]:
                value1 = f.formatValue(param)
                value2 = g.formatValue(param)
                line = "%-40s %-30s %-30s \n"%(param,value1,value2)
                gOutput += line if value1==value2 else apy.shell.textc(line,'r')
        if gOutput!='':
            output += "%%---- %s\n"%group['name'] + gOutput + "\n";
    print( output )
