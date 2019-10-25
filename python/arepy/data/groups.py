import numpy as np
import arepy as apy

class collection:
    """Collection of groups"""
    def __init__(self,names=None,options=None,**opt):
        self.items = {}        # list of groups
        self.order =  []        # ordered list of group names, because dict.keys() is not ordered
        self.size =   0         # number of groups
        self.current = 0        # iterator pointer
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
        if name not in self.items:
            self.addGroup(name)
        return self.items[name]

    # object iterator
    def __iter__(self):
        self.current = 0
        return self
    def __next__(self):
        if self.current < self.size:
            item = self.order[self.current]
            self.current += 1
            return self.items[item]
        else:
            raise StopIteration
    
    def _addGroup(self): # this can be overloaded when the class is inherited
        return group(**self.opt)
    def addGroup(self,name,options=None):
        name = str(name)
        self.items[name] = self._addGroup()
        self.items[name].index = self.size
        self.items[name].name = name
        self.order.append(name)
        self.size += 1
        if options is not None:
            self.items[name].opt.update(options)
                    
    def items(self):
        return [self.items[g] for g in self.order]
    
    def keys(self):
        return self.order

    def _setOptions(self,opt,values):
        for index,name in enumerate(self.order):
            self.items[name].opt[opt] = values[index]
    def setOptions(self,opt,values=None):
        if isinstance(opt,dict):
            for key,values in opt.items():
                self._setOptions(key,values)
        else:
            self._setOptions(opt,values)

    def foreach(self,fn,args=[],cache=None,nproc=None,append=False):
        print(self.opt)
        apy.shell.exit('This needs to be implemented')
        '''
        nproc = self.opt['nproc'] if nproc is None else nproc
        cache = self.opt['cache'] if cache is None else cache
        arguments = [[item]+args for item in self.items]
        if cache:
            dirCache = self.opt['dirCache']
            label = cache
        else:
            dirCache = None
            label = self.name
        self.data[fn.__name__] = apy.data.foreach(fn,arguments,nproc=nproc,label=label,append=append,
                                                  dirCache=dirCache)
        return self.data[fn.__name__]        
        '''
        
class group:
    """Group of items"""

    def __init__(self,*args,**opt):
        self.index = None        # group index
        self.name = ''           # group name
        self.items = []          # list of items
        self.size =  0           # number of items
        self.current = 0         # iterator pointer
        self.data =  {}          # group data
        self.opt = {            
            'cache':     False,  # cache calculated data
            'dirCache':  './',   # direction of the cache
            'nproc':     1,      # number of processors for figures
            'n_jobs':    1,      # number of processors for KDTree
        }
        self.opt.update(opt)

        if args:
            self.addItem(*args)

    # object selector
    def __getitem__(self,item):
        return self.items[item]

    # object iterator
    def __iter__(self):
        self.current = 0
        return self
    def __next__(self):
        if self.current < self.size:
            self.current += 1
            return self.items[self.current-1]
        else:
            raise StopIteration

    def _addItem(self,*args): # this can be overloaded when the class is inherited
        return item(self.size,self.name,*args)
    def addItem(self,*args):
        self.items.append( self._addItem(*args) )
        self.size += 1

    def _setOptions(self,opt,values):
        for index,group in enumerate(self.order):
            self.opt[opt] = values
    def setOptions(self,opt,values=None):
        if isinstance(opt,dict):
            for key,values in opt.items():
                self._setOptions(key,values)
        else:
            self._setOptions(opt,values)
        
    def foreach(self,fn,args=[],cache=None,update=False,nproc=None,append=False):
        """Parallelized for-each-item loop
        """
        nproc = self.opt['nproc'] if nproc is None else nproc
        cache = self.opt['cache'] if cache is None else cache
        arguments = [[item]+args for item in self.items]
        dirCache = self.opt['dirCache'] if cache else None
        label = cache if cache else self.name
        self.data[fn.__name__] = apy.data.foreach(fn,arguments,nproc=nproc,label=label,append=append,
                                                  dirCache=dirCache,update=update)
        return self.data[fn.__name__]        

class item:
    """Item of a group"""
    def __init__(self,itemIndex,groupName,opt):
        self.index = itemIndex
        self.groupName = groupName
        self.opt = opt
