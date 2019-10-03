import numpy as np
import arepy as apy
import os

class sink():

    def __enter__(self):
        return self
        
    def __exit__(self, type, value, tb):
        return

    def __init__(self,fileName='',simplex=False,varAccRad=False,accLum=False,sinkFeed=False,intPad=1,
                 order='FormationOrder',reverse=False, verbose=False):
        self.simplex = simplex
        self.varAccRad = varAccRad
        self.accLum = accLum
        self.sinkFeed = sinkFeed
        self.intPad = intPad
        self.verbose = verbose
        self.fileName = fileName
        
        self.props = {} 
        self.propsOrder = []  # we have to store also correct order of the parameters
        self._initProp('Pos', {'dim': 3, 'vector': True, 'dtype': np.float64}) 
        self._initProp('Vel', {'dim': 3, 'vector': True, 'dtype': np.float64}) 
        self._initProp('Acc', {'dim': 3, 'vector': True, 'dtype': np.float64}) 
        self._initProp('Mass', {'dim': 1, 'vector': False, 'dtype': np.float64}) 
        if self.simplex:
            self._initProp('MassOld', {'dim': 1, 'vector': False, 'dtype': np.float64}) 
        if self.varAccRad:
            self._initProp('AccretionRadius', {'dim': 1, 'vector': False, 'dtype': np.float64}) 
        self._initProp('FormationMass', {'dim': 1, 'vector': False, 'dtype': np.float64}) 
        self._initProp('FormationTime', {'dim': 1, 'vector': False, 'dtype': np.float64}) 
        if self.accLum:
            self._initProp('AccretionRate', {'dim': 1, 'vector': False, 'dtype': np.float64}) 
            self._initProp('TimeOld', {'dim': 1, 'vector': False, 'dtype': np.float64}) 
        self._initProp('ID', {'dim': 1, 'vector': False, 'dtype': np.uint64}) 
        self._initProp('HomeTask', {'dim': 1, 'vector': False, 'dtype': np.uint32}) 
        self._initProp('Index', {'dim': 1, 'vector': False, 'dtype': np.uint32}) 
        self._initProp('FormationOrder', {'dim': 1, 'vector': False, 'dtype': np.uint32}) 
        if self.sinkFeed:
            self._initProp('N_sne', {'dim': 1, 'vector': False, 'dtype': np.uint32}) 
            self._initProp('explosion_time', {'dim': sinkFeed, 'vector': False, 'dtype': np.float64}) 
        if self.intPad>0:
            self._initProp('padding', {'dim': 1, 'vector': False, 'dtype': np.uint32}) 
        self.nProps = len(self.props)

        self.nSinks = 0
        self.snapTime = 0

        if fileName is not '':
            self.read(fileName,order=order,reverse=reverse)

    def _initProp(self,name,values):
        self.props[name] = values
        self.propsOrder.append(name)
            
    def order(self,order,reverse=False):
        ids = np.argsort(self.props[order]['data'])
        if reverse:
            ids = ids[::-1]
        for prop in self.propsOrder:
            self.props[prop]['data'] = self.props[prop]['data'][ids]
        
    def read(self,fileName,order='FormationOrder',reverse=False):
        if self.verbose:
            print( apy.shell.textc("Reading sink file: %s"%fileName,'yellow') )
        if not os.path.isfile(fileName):    
            apy.shell.exit('File \"%s\"\n       does not exist not found'%fileName)
        with open(fileName, mode='rb') as f:
            self.fileName = fileName
            self.snapTime = np.fromfile(f, np.float64, 1)[0]
            self.nSinks = np.fromfile(f, np.uint32, 1)[0]
            self.props3D = []
            for prop in self.propsOrder:
                if self.props[prop]['dim']>1:
                    shape = (self.nSinks,self.props[prop]['dim'])
                else: 
                    shape = self.nSinks
                self.props[prop]['data'] = np.zeros(shape,dtype=self.props[prop]['dtype'])
            for i in np.arange(self.nSinks):            
                for prop in self.propsOrder:
                    dim = self.props[prop]['dim']
                    data = np.fromfile(f, self.props[prop]['dtype'], dim)
                    if dim>1:
                        self.props[prop]['data'][i,:] = data.reshape(1, dim)[0]
                    else:
                        self.props[prop]['data'][i] = data[0]
        if order!=None:
            self.order(order,reverse=reverse)

    def write(self,fileName):
        if self.verbose:
            print( apy.shell.textc("Writing sink file: %s"%fileName,'yellow') )
        with open(fileName, mode='w') as f:
            self.fileName = fileName
            self.snapTime.astype( np.float64 ).tofile(f)
            self.nSinks.astype( np.uint32 ).tofile(f)
            for i in np.arange(self.nSinks):
                for prop in self.propsOrder:
                    self.props[prop]['data'][i].astype( self.props[prop]['dtype'] ).tofile(f)

    def show(self,props=['ID','FormationOrder','Mass','FormationTime','Pos'],
             order=None, reverse=False, limit=None, convert=None, offset=None):
        if order!=None:
            self.order(order,reverse=reverse)
        nProps = len(props)
        data = []
        headers = []
        for i,prop in enumerate(props):
            if self.props[prop]['vector']:
                headers.append(prop+' X')
                headers.append(prop+' Y')
                headers.append(prop+' Z')
                headers.append(prop+' R')
            else:
                headers.append(prop)
        if limit==None:
            limit = self.nSinks
        for s in range(limit):
            sinkData = []
            for i,prop in enumerate(props):
                conv = 1.0 if (convert==None) or prop not in convert else convert[prop]
                offs = 0.0 if (offset==None) or prop not in offset else offset[prop]
                value = self.props[prop]['data']
                if self.props[prop]['vector']:
                    if offs==0.0: offs = [0.,0.,0.]
                    sinkData.append( (value[s,0]-offs[0])*conv )
                    sinkData.append( (value[s,1]-offs[1])*conv )
                    sinkData.append( (value[s,2]-offs[2])*conv )
                    sinkData.append( np.linalg.norm(value[s,:]-offs)*conv )
                else:
                    sinkData.append( (value[s]-offs)*conv )
            data.append( sinkData )
        print( 'SnapFile:', self.fileName )
        print( 'SnapTime:', self.snapTime )
        print( apy.data.tabulate(data,headers=headers) )

    def setValues(self,prop,values,order=None,reverse=False):
        if order is not None:
            self.order(order,reverse=reverse)
        self.props[prop]['data'] = values

    def getValues(self,props,order=None,reverse=False,limit=None,dictionary=False):
        if order is not None:
            self.order(order,reverse=reverse)
        ids = slice(0,self.nSinks if limit is None else limit)
        def fn(prop):
            if prop=='SnapTime':            # snapshot time
                return np.full(self.nSinks,self.snapTime)
            elif prop=='MassCenterRadius':  # radius to the center of the sink mass
                mass = self.props['Mass']['data']
                pos = self.props['Pos']['data']
                massCenter = np.sum(pos.T*mass,axis=1)/np.sum(mass)
                return np.linalg.norm(pos-massCenter,axis=1)
            else:
                return self.props[prop]['data'][ids] if prop in self.props else None
        if isinstance(props,(str,int,float)) and dictionary==False:
            return fn(props)
        else:
            return { prop:fn(prop) for prop in props }

    def getEmpty(self,prop):
        return np.zeros(self.props[prop]['dim'],dtype=self.props[prop]['dtype'])
