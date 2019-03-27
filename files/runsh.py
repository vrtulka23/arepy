import numpy as np
import arepy as apy
import re
from subprocess import call

class runsh():
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        True

    def __init__(self,fileName=None,show=False,notes=False):
        self.groups = [
            {'name':"Other options",
             'params':['ANALYZE_DIR']},
            {'name':"Cluster options",
             'params':['NUM_NODES','NUM_PROC','JOB_WALL_TIME','JOB_TYPE','FLAGS_RUN','FLAGS_RESTART']},
            {'name':"Arepo Images",
             'params':['IMAGE_NODES','IMAGE_PROC','IMAGE_WALLTIME','IMAGE_TYPE','IMAGE_FLAGS']},
        ]
        self.params = {
            'ANALYZE_DIR':    {'dtype':'s','default':"default",         'format':'%s'},
            'NUM_NODES':      {'dtype':'i','default':1,                 'format':'%d'},
            'NUM_PROC':       {'dtype':'i','default':16,                'format':'%d'},
            'JOB_WALL_TIME':  {'dtype':'s','default':"8:00:00",         'format':'%s'},
            'JOB_TYPE':       {'dtype':'s','default':"standard",        'format':'%s'},
            'FLAGS_RUN':      {'dtype':'s','default':"",                'format':'%s'},
            'FLAGS_RESTART':  {'dtype':'s','default':"1",               'format':'%s'},

            'IMAGE_NODES':    {'dtype':'i','default':1,                 'format':'%d'},
            'IMAGE_PROC':     {'dtype':'i','default':40,                'format':'%d'},
            'IMAGE_WALLTIME': {'dtype':'s','default':"1:00:00",         'format':'%s'},
            'IMAGE_TYPE':     {'dtype':'s','default':"fat",             'format':'%s'},
            'IMAGE_FLAGS':    {'dtype':'a','default':(0,10,0,1,0,1,0,1),'format':'%d %d %f %f %f %f %f %f'},
        }

        if fileName!=None:
            self.read(fileName,show=show,notes=notes)

    def parse(self, rmGroups=[], rmParams=[], cmGroups=[], cmParams=[]):
        output = ''
        for group in self.groups:
            if group['name'] in rmGroups: continue
            gOutput = ''
            for param in group['params']:
                if param in rmParams: continue
                if 'value' in self.params[param]:
                    if (param in cmParams) or (group['name'] in cmGroups):
                        gOutput += "# "
                    if (self.params[param]['dtype']=='s'):
                        gOutput += "%s=\"%s\""%(param,self.params[param]['format']%self.params[param]['value'])
                    elif (self.params[param]['dtype']=='a'):
                        gOutput += "%s=(%s)"%(param,self.params[param]['format']%self.params[param]['value'])
#                    elif (self.params[param]['dtype']=='r'):
#                        gOutput += """FLAGS_IMAGE=()
#for i in {%d..%d}
#do
#    FLAGS_IMAGE+=(\"5 $i 1000 1000 0 1 2 %f %f %f %f %f %f\")
#done"""%self.params[param]['value']
                    else:
                        gOutput += "%s="%(param) 
                        gOutput += self.params[param]['format']%self.params[param]['value'] 
                    if 'note' in self.params[param]:
                        gOutput += '   % '+self.params[param]['note']
                    gOutput += '\n'
                    
            if gOutput!='':
                output += "# %s\n"%group['name'] + gOutput + "\n";
        return output

    '''
    def read(self,fileName,show=False,notes=False):
        with open(fileName,'r') as f:
            content = f.read()
        lines = content.split("\n")
        for line in lines:
            m = re.match("([_A-Z0-9]+)[=]?([\.\e\+\-0-9]*)\s*[\#]?(.*)",line)

            if m==None: continue
            note = m.group(3) if notes else None
            self.setValue(m.group(1),m.group(2),note)
        
        if show==True:
            print( self.parse() )
    '''

    def write(self,fileName,rmGroups=[],rmParams=[],cmGroups=[],cmParams=[]):
        output = "#!/bin/bash \n\n"
        output += self.parse(rmGroups=rmGroups,rmParams=rmParams,cmGroups=cmGroups,cmParams=cmParams)
        output += "\nsource $bits/arepo/run.main.sh"
        with open(fileName,'w') as f:
            f.write(output)
            call(['chmod','+x',fileName])

    def setValue(self,param,value=None,note=None):
        if isinstance(param,dict):
            for p,v in param.items():
                self._setValue(p,v)
        else:
            self._setValue(param,value,note)

    def _setValue(self,param,value=None,note=None):
        if param in self.params:
            dtype = self.params[param]['dtype']
            if (dtype=='e'):
                value = ''
            else:
                if (value==None): 
                    value = self.params[param]['default']
                if (dtype=='i'):
                    value = 0 if value=='' else int(value)
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

    def getValue(self,param):
        return self.params[param]['value'] if value in self.params[param] else None
