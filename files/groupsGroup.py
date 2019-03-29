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
    def _foreach(self,fn,cols,nproc,args):
        ncols = cols if isinstance(cols,int) else len(cols)
        fnName = fn.__name__
        pb = apy.util.pb(vmax=self.size,label=fnName+' '+self.name)
        if nproc>1:
            arguments = [[item]+args for item in self.items()]
            results = apy.util.parallelPool(fn,arguments,pbar=pb,nproc=nproc)
        data = []
        for item in self.items():
            result = results[item.index] if nproc>1 else fn(item,*args)
            result = [result] if ncols==1 else result
            for c in range(ncols):
                part = np.array(result[c])
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
    def foreach(self,fn,cols=1,cache=False,nproc=1,args=[]):
        if cache:
            apy.shell.mkdir(self.opt['dirCache'],opt='u')
            nameCache = self.opt['nameCache']+'_'+fn.__name__+'_'+self.name
            return apy.data.cache( self._foreach, nameCache, cacheDir=self.opt['dirCache'], args=[fn,cols,nproc,args])
        else:
            return self._foreach(fn,cols,nproc,args)

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
        
    # Set coordinate transformations for every item
    def setTransf(self,**opt):
        for item in self.items():
            nopt = {}
            for k,v in opt.items():
                nopt[k] = v[item.index] if np.ndim(v)>1 else v
            item.setTransf(**nopt)
            
    # Common plotting routines 
    # Add multiple objects to the canvas

    # Plot Arepo image
    def setImage(self, axis, prop, imgType, norm=None, normType=None, cmap=None):
        def setImage(item):
            im,px,py = item.sim.getImage(item.snap,prop,imgType)
            if prop=='density':
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
            normType = 'log' if prop in logNormsProps else 'lin'
        norm = 'img_%s_%s'%(prop,imgType) if norm is None else norm
        extent = self.transf.convert('moveOrigin',data['extent'],[0,0,1,1])
        axis.setImage(data=data['im'],extent=extent,norm=norm,normType=normType,cmap=cmap)

    # Add projection image
    def setProjection(self, axis, prop, bins=200, cache=False, nproc=1, norm=None, normType=None, cmap=None):
        proj = self.foreach(setProjection,['data','extent'],args=[prop,bins],cache=cache,nproc=nproc)
        if isinstance(axis,list):
            for i in range(len(axis)):
                data = proj['data'][:,i]
                n = norm[i] if isinstance(norm,list) else norm
                nt = normType[i] if isinstance(normType,list) else normType
                c = cmap[i] if isinstance(cmap,list) else cmap
                axis[i].setImage(data=data, extent=proj['extent'], norm=n, normType=nt, cmap=c)
        else:
            axis.setImage(data=proj['data'],extent=proj['extent'], norm=norm, normType=normType, cmap=cmap)

    # Add times to the plot
    def addTimes(self, axis, **opt):
        def addTimes(item):
            with item.getSnapshot() as sn:
                time = item.sim.units.guess('time',sn.getHeader('Time'),utype='old')
            return 't = %s'%time
        values = self.foreach(addTimes,1)
        nopt = {'loc':'top left'}
        nopt.update(opt)
        axis.addText(values,**nopt)

    # Add redshift to the plot
    def addRedshifts(self, axis, **opt):
        def addRedshifts(item):
            with item.getSnapshot() as sn:
                z = 1./sn.getHeader('Time')-1.
            return 'z = %.03f'%z
        values = self.foreach(addRedshifts)
        nopt = {'loc':'top left'}
        nopt.update(opt)
        axis.addText(values,**nopt)

    # Add snapshot number to the plot
    def addSnapNums(self, axis, **opt):
        def addSnapNums(item):
            return '%03d'%item.snap
        values = self.foreach(addSnapNums)      
        nopt = {'loc':'top left'}
        nopt.update(opt)
        axis.addText(values,**nopt)    

    # Add particle scatter plot
    def addParticles(self, axis, ptype, **opt):
        coords = []
        for item in self.items():
            with item.getSnapshot() as sn:
                center = item.transf['preselect']['center']
                radius = item.transf['preselect']['radius']
                ids, r2 = sn.getProperty(ptype,{'name':'RadialRegion',"center":center,'radius':radius})
                coord = sn.getProperty(ptype,'Coordinates',ids=ids)
            coord = item.transf.convert(['translate','align','flip','rotate','postselect'],coord)
            coords.append( coord * item.sim.units.conv['length'] )
        x = [coord[:,0] for coord in coords]
        y = [coord[:,1] for coord in coords]
        nopt = {'s':20,'marker':'+','c':'black','edgecolors':None,'linewidths':1}
        nopt.update(opt)
        if isinstance(axis,list):
            for i in range(len(axis)):
                axis[i].addScatter(x,y,**nopt)
        else:
            axis.addScatter(x,y,**nopt)

    # Add coordinate system with axes and angles
    def addCoordSystem(self, axis, info=False, vector=None):
        colors = ['red','blue','gold','black']
        def addCoordSystem(item,vector):
            box = item.transf['postselect']['box']
            size = np.min((box[1::2]-box[::2]) * 0.5 * item.sim.units.conv['length'])
            coord = [[size,0,0],[0,size,0],[0,0,size]]
            if 'align' in item.transf.items:   # show the alignment vector
                vector = item.transf.items['align']['vector']
                vector = vector/np.linalg.norm(vector)*size
                coord.append(vector)
            elif vector is not None:           # show arbitrary vector
                vector = vector/np.linalg.norm(vector)*size
                coord.append(vector)                
            u,v,w = item.transf.convert(['align','flip','rotate'],np.array(coord)).T
            return u,v
        u,v = self.foreach(addCoordSystem,2,args=[vector])
        for i in range(len(u[0])):
            axis.addQuiver(0,0,u[:,i],v[:,i],color=colors[i],pivot='tail',angles='xy',scale=1,scale_units='xy')
        
        if info:         # print information about rotations
            info = []
            for item in self.items():
                text = ''
                if 'align' in item.transf.items:
                    text += "%.1f,%.1f,%.1f = A\n"%tuple(item.transf['align']['angles'])
                if 'flip' in item.transf.items:
                    text += "%d,%d,%d = F\n"%tuple(item.transf['flip']['axes'])
                if 'rotate' in item.transf.items:
                    text += "%.1f,%.1f,%.1f = R\n"%tuple(item.transf['rotate']['angles'])
                info.append( text[:-1] )
            axis.addText(info,loc='bottom right',fontsize=6)

    # Create a 2D property histogram
    def addHistogram2D(self, axis, ptype, xprop, yprop, bins, norm=None, normType='lin',
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
        axis.setImage(data=allData,extent=extent,norm=norm,normType=normType,cmap=cmap,aspect=aspect)

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
############################################
# Local functions that can be parallelized #
############################################

# Get projection of a region in the snapshot
def setProjection(item,prop,bins):
    snap = item.getSnapshot()
    data = snap.getProperty(0,{'name':'BoxProjection','transf':item.transf,'w':prop,'bins':bins})
    extent = item.transf['postselect']['box'][:4] * item.sim.units.conv['length']
    return data,extent
