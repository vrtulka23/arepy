import numpy as np
import arepy as apy
from arepy.files.groupsGroup import *

################
# Groups class #
################
class groups:
    def __init__(self,names=None,options=None,**opt):
        self.groups = {}        # list of groups
        self.order =  []        # ordered list of group names, because dict.keys() is not ordered
        self.size =   0         # number of groups
        self.opt =    opt       # some additional settings

        if names is not None:
            if isinstance(options,dict):   # names ... options
                for name in names:
                    self.addGroup(name)
                self.setOptions(options)
            elif isinstance(options,list): # header ... settings
                for opt in options:
                    self.addGroup( opt[0], dict(zip(names[1:],opt[1:])) )
            else:
                for name in names:         # names
                    self.addGroup(name) 

    # select group
    def __getitem__(self,name):
        name = str(name)
        if name not in self.groups:
            self.addGroup(name)
        return self.groups[name]

    def addGroup(self,name,options=None):
        name = str(name)
        self.groups[name] = group(**self.opt)
        self.groups[name].index = self.size
        self.groups[name].name = name
        self.order.append(name)
        self.size += 1
        if options is not None:
            self.groups[name].opt.update(options)
                    
    def items(self):
        return [self.groups[g] for g in self.order]
    
    def keys(self):
        return self.order

    def _setOptions(self,opt,values):
        for index,name in enumerate(self.order):
            self.groups[name].opt[opt] = values[index]
    def setOptions(self,opt,values=None):
        if isinstance(opt,dict):
            for key,values in opt.items():
                self._setOptions(key,values)
        else:
            self._setOptions(opt,values)
        
