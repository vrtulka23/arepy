import numpy as np
import arepy as apy
from arepy.files.groupsItem import *

###############
# Group class #
###############
class group:
    def __init__(self,sim=None,snaps=None,**opt):
        self.index = None     # group index
        self.name = ''        # group name
        self.snaps = []       # list of snapshots
        self.size =  0        # number of snapshots
        self.data =  {}       # group data
        self.opt = {
            'dirCache':  './',                                        # direction of the cache
            'nameCache': self.name if self.name=='' else 'group',     # name of the cache file
        }
        self.opt.update(opt)
        
        if sim is not None:
            self.addSnapshot(sim,snaps)

    # select group
    def __getitem__(self,snap):
        return self.snaps[snap]

    def addSnapshot(self,sim,snaps):
        snaps = map(int,[snaps] if np.isscalar(snaps) else snaps)
        for s in snaps:
            self.snaps.append( item(self.size,sim,int(s),self.name) )
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

    def items(self):
        return self.snaps
        
    # This method returns an array of calculated values for each returned value from 'fn()'
    # The 'self.data' array has dimensions of (c,s) or (s) if 'fn()' returns only one value
    def _foreach(self,fn,cols,args):
        ncols = cols if isinstance(cols,int) else len(cols)
        fnName = fn.__name__
        data = []
        pb = apy.util.pb(vmax=self.size,label=fnName+' '+self.name)
        for item in self.items():
            results = fn(item,*args)
            if ncols==1: results = [results]
            for c in range(ncols):
                part = np.array(results[c])
                if item.index==0:
                    emptydata = np.zeros( (self.size,)+part.shape, dtype=part.dtype)
                    data.append( emptydata )
                data[c][item.index] = part
            pb.increase()
        pb.close()
        if ncols==1:
            self.data[fnName] = data[0]
        elif isinstance(cols,list):
            self.data[fnName] = {cols[i]:data[i] for i in range(ncols)} 
        else:
            self.data[fnName] = data
        return self.data[fnName]
    def foreach(self,fn,cols=1,cache=False,args=[]):
        if cache:
            apy.shell.mkdir(self.opt['dirCache'],opt='u')
            nameCache = self.opt['nameCache']+'_'+fn.__name__+'_'+self.name
            return apy.data.cache( self._foreach, nameCache, cacheDir=self.opt['dirCache'], args=[fn,cols,args])
        else:
            return self._foreach(fn,cols,args)

    #########################
    # Common data reduction #
    ######################### 
    
    def getPropertyRange(self, ptype, prop, scale='lin'):
        ranges = np.zeros((self.size,2))
        pb = apy.util.pb(vmax=self.size,label='Calculating range (%s)'%(prop))
        for item in self.items():
            with item.getSnapshot() as sn:
                if scale=='lin':
                    res = sn.getProperty(ptype,['Minimum','Maximum'],args={'p':prop})
                    ranges[item.index,0] = res[0].min()
                    ranges[item.index,1] = res[1].max()
                elif scale=='log':
                    res = sn.getProperty(ptype,['MinPos','Maximum'],args={'p':prop})
                    ranges[item.index,0] = np.log10(res[0].min())
                    ranges[item.index,1] = np.log10(res[1].max())
            pb.increase()
        pb.close()
        return np.sum(ranges,axis=0)

    # Create a list of sink particles with their properties in each snapshot
    def getSinkProps(self,props,selectIDs=None,**opt):
        props = [props] if isinstance(props,str) else props
        data = {}
        pb = apy.util.pb(vmax=self.size,label='Reading sink properties')
        for item in self.items():
            with item.getSink(**opt) as sn:
                sids = sn.getValues('ID')
                pdata = sn.getValues(props)
                for i,sid in enumerate(sids):
                    if selectIDs is not None and sid not in selectIDs:
                        continue
                    sid = str(int(sid))
                    if sid not in data:
                        data[sid] = {prop:[] for prop in props}
                    for p,prop in enumerate(props):
                        data[sid][prop].append(pdata[p][i])
            pb.increase()
        pb.close()
        for sid in data.keys():
            for prop in props:
                data[sid][prop] = np.array(data[sid][prop])
        return data
        
    # Set coordinate transformations and regions
    def setTransf(self,**opt):
        for item in self.items():
            nopt = {}
            if 'box' in opt:
                nopt['box'] = opt['box'][item.index] if np.ndim(opt['box'])>1 else opt['box']
            elif 'center' in opt:
                nopt['center'] = opt['center'][item.index] if np.ndim(opt['center'])>1 else opt['center']
                if 'radius' in opt:
                    nopt['radius'] = opt['radius'][item.index] if np.ndim(opt['radius'])>1 else opt['radius']
                elif 'size' in opt:
                    nopt['size'] = opt['size'][item.index] if np.ndim(opt['size'])>1 else opt['size']
            if 'origin' in opt:
                nopt['origin'] = opt['origin'][item.index] if np.ndim(opt['origin'])>1 else opt['origin']
            if 'angles' in opt:
                nopt['angles'] = opt['angles'][item.index] if np.ndim(opt['angles'])>1 else opt['angles']
            item.setTransf(**nopt)
            
    # Common plotting routines 
    # Add multiple objects to the canvas

    # Plot Arepo image
    def setImage(self,sp, imgProperty, imgType, norm=None, normType=None, cmap=None):
        def setImage(item):
            im,px,py = item.sim.getImage(item.snap,imgProperty,imgType)
            if imgProperty=='density':
                im *= item.sim.units.conv['density']
            if 'boxSize' not in item.sim.optImages:
                apy.shell.exit("No 'boxSize' option for simulation %d (groups.py)"%item.index)
            box = item.sim.optImages['boxSize']
            extent = np.array(box[:4]) * item.sim.units.conv['length']
            center = (box[::2]+box[1::2])*0.5 * item.sim.units.conv['length']
            return im,extent,center,box
        data = self.foreach(setImage,['im','extent','center','box'])
        self.setRegion(data['box'])
        self.setTransf('moveOrigin','translate', origin=data['center'])
        logNormsProps = ['density','rih','ndens']
        if not normType:
            normType = 'log' if imgProperty in logNormsProps else 'lin'
        norm = 'img_%s_%s'%(imgProperty,imgType) if norm is None else norm
        extent = self.transf.convert('moveOrigin',data['extent'],[0,0,1,1])
        sp.setImage(data=data['im'],extent=extent,norm=norm,normType=normType,cmap=cmap)
        sp.setOption(xlim=extent[:,:2], ylim=extent[:,2:])

    # Add projection image
    def setProjection(self, sp, imgProperty, bins=200, rot=None,
                      norm=None, normType=None, cmap=None):
        def setProjection(item):
            snap = item.getSnapshot()
            dens = snap.getProperty(0,{'name':'BoxProjection','transf':item.transf,
                                       'w':imgProperty,'bins':bins})
            extent = item.transf['postselect']['box'][:4] * item.sim.units.conv['length']
            return dens,extent
        data = self.foreach(setProjection,['dens','extent'],cache=False)
        sp.setImage(data=data['dens'],extent=data['extent'],norm=norm,normType=normType,cmap=cmap)
        sp.setOption(xlim=data['extent'][:,:2], ylim=data['extent'][:,2:])

    # Add times to the plot
    def addTimes(self,sp,**opt):
        def addTimes(item):
            with item.getSnapshot() as sn:
                time = item.sim.units.guess('time',sn.getHeader('Time'),utype='old')
            return 't = %s'%time
        values = self.foreach(addTimes,1)
        nopt = {'loc':'top left'}
        nopt.update(opt)
        sp.addText(values,**nopt)

    # Add redshift to the plot
    def addRedshifts(self,sp,**opt):
        def addRedshifts(item):
            with item.getSnapshot() as sn:
                z = 1./sn.getHeader('Time')-1.
            return 'z = %.03f'%z
        values = self.foreach(addRedshifts,1)
        nopt = {'loc':'top left'}
        nopt.update(opt)
        sp.addText(values,**nopt)

    # Add snapshot number to the plot
    def addSnapNums(self,sp,loc='top right'):
        def addSnapNums(item):
            return '%03d'%item.snap
        values = self.foreach(addSnapNums,1)      
        sp.addText(values,loc)    

    # Add particle scatter plot
    def addParticles(self, sp, ptype, **nopt):
        coords = []
        for item in self.items():
            with item.getSnapshot() as sn:
                if 'postselect' in item.transf.items:
                    box = item.transf['preselect']['box']
                    ids, coord = sn.getProperty(ptype,{'name':'BoxRegion',"box":box})
                else:
                    coord = sn.getProperty(ptype,'Coordinates')
            coord = item.transf.convert('translate',coord)
            if 'rotate' in item.transf.items:
                coord = item.transf.convert('rotate',coord)
            coords.append( coord * item.sim.units.conv['length'] )
        x = [coord[:,0] for coord in coords]
        y = [coord[:,1] for coord in coords]
        opt = {'s':20,'marker':'+','c':'black','edgecolors':None,'linewidths':1}
        opt.update(nopt)
        sp.addScatter(x,y,**opt)

    # Create a 2D property histogram
    def addHistogram2D(self, sp, ptype, xprop, yprop, bins, norm=None, normType='lin',
                       xscale='lin', yscale='lin', cmap=None, aspect='auto'):
        if isinstance(bins,int): bins = [bins,bins]
        if isinstance(bins[0],int):
            xr = self.getPropertyRange(ptype, xprop, xscale)
            yr = self.getPropertyRange(ptype, yprop, yscale)
            bins[0] = np.linspace(xr[0],xr[1],bins[0]) if xscale=='lin' else np.logspace(xr[0],xr[1],bins[0])
            bins[1] = np.linspace(yr[0],yr[1],bins[1]) if yscale=='lin' else np.logspace(yr[0],yr[1],bins[1])
        args = {"x":xprop,'y':yprop,'bins':bins,'xscale':xscale,'yscale':yscale}            
        allData = []
        pb = apy.util.pb(vmax=self.size,label='Calculating histogram (%s,%s)'%(xprop,yprop))
        for item in self.items(): 
            with item.getSnapshot() as sn:
                hist = sn.getProperty(ptype,'Histogram2D',args=args)
            allData.append( hist )
            pb.increase()
        pb.close()
        xext = [bins[0][0],bins[0][-1]]
        yext = [bins[1][0],bins[1][-1]]
        if xscale=='log': xext = np.log10(xext)
        if yscale=='log': yext = np.log10(yext)
        extent = [xext[0],xext[1], yext[0],yext[1]]
        norm = 'hist_%s_%s'%(xprop,yprop) if norm is None else norm
        sp.setImage(data=allData,extent=extent,norm=norm,normType=normType,cmap=cmap,aspect=aspect)
        sp.setOption(xlim=extent[:2], ylim=extent[2:])

    '''
    # Interpolate snapshots according to their times
    def getInterpSnapTimes(self,bins=None):
        allSnaps, allTimes = [], []
        trange = np.zeros((self.nSims,4))
        for s,sim in enumerate(self.sims):
            snaps = sim.getSnapNums()
            times = np.array([sim.getSnapshot(snap).getHeader('Time') for snap in snaps])
            allSnaps.append( snaps )
            allTimes.append( times )
            trange[s,:3] = [ times.min(), times.max(), len(times) ]
        tmin, tmax = np.max(trange[:,0]), np.min(trange[:,1])
        if bins==None: # calculates maximum common number of snapshots for all sims
            for s in range(self.nSims):
                trange[s,3] = ((tmin<=allTimes[s]) & (allTimes[s]<=tmax)).sum()
            bins = int(trange[:,3].min())
        times = np.linspace(tmin,tmax,bins)
        snaps = np.zeros((self.nSims,bins))
        for s in range(self.nSims):
            snaps[s] = np.interp(times,allTimes[s],allSnaps[s])        
        return times, np.around(snaps).astype(int)
    '''
