import numpy as np
import arepy as apy
import arepy.data.groups as dataGroups

#############################
# Overload collection class #
#############################
class collection(dataGroups.collection):
    def __init__(self,names=None,options=None,**opt):
        super().__init__(names=names,options=options,**opt)

    def _addGroup(self):
        return group(**self.opt)
        
########################
# Overload group class #
########################
class group(dataGroups.group):
    def __init__(self,sim=None,snaps=None,**opt):
        super().__init__(**opt)

        if sim is not None:
            self.addSnapshot(sim,snaps)

    def _addItem(self,opt,sim,snap): 
        return item(self.size,self.name,opt,sim,snap)

    def addSnapshot(self,sim,snaps,opt=None):
        snaps = [int(snaps)] if np.isscalar(snaps) else [int(s) for s in snaps]
        if opt is None or isinstance(opt,dict):
            opt = [opt]*len(snaps) 
        for i,s in enumerate(snaps):
            self.addItem(opt[i],sim,int(s))

    #########################
    # Common data reduction #
    ######################### 

    def getPropertyRange(self, prop, scale='lin'):
        ranges = np.zeros((self.size,2))
        pb = apy.shell.pb(vmax=self.size,label='Calculating range (%s)'%(prop))
        for item in self.items:
            with item.getSnapshot() as sn:
                if scale=='lin':
                    res = sn.getProperty([{'name':'Minimum','p':prop},{'name':'Maximum','p':prop}])
                    ranges[item.index,0] = res[0].min()
                    ranges[item.index,1] = res[1].max()
                elif scale=='log':
                    res = sn.getProperty([{'name':'MinPos','p':prop},{'name':'Maximum','p':prop}])
                    ranges[item.index,0] = np.log10(res[0].min())
                    ranges[item.index,1] = np.log10(res[1].max())
            pb.increase()
        pb.close()
        return np.sum(ranges,axis=0)

    # Create a list of sink particles with their properties in each snapshot
    def getSinkProps(self,props,select=None):
        # get properties
        props = [props] if isinstance(props,str) else props
        if 'FormationOrder' not in props: props.append('FormationOrder')
        if 'ID' not in props:             props.append('ID')
        pdata = self.foreach(getSinkProps,args=[props,select],append=True)
        # stack values on each other
        for prop in props:
            if prop in ['Pos','Vel','Acc']:
                pdata[prop] = np.vstack(pdata[prop])
            else:
                pdata[prop] = np.hstack(pdata[prop])
        # re-arrange according to the formation order
        nsinks = int(np.max(pdata['FormationOrder']))
        sdata = [None]*nsinks
        for i in range(nsinks):
            ids = pdata['FormationOrder']==i+1
            if np.sum(ids)==0: continue
            sdata[i] = {key:pdata[key][ids] for key in props}
            sdata[i]['FormationOrder'] = int(sdata[i]['FormationOrder'][0])
            sdata[i]['ID'] = int(sdata[i]['ID'][0])
        return sdata

    ##################################
    # Common transformation routines #
    ##################################
        
    # Set coordinate transformations for every item
    def setTransf(self,**opt):
        for item in self.items:
            nopt = {}
            for k,v in opt.items():
                if k in ['size']:
                    nopt[k] = v if np.isscalar(v) else v[item.index]
                else:
                    nopt[k] = v[item.index] if np.ndim(v)>1 else v
            item.setTransf(**nopt)

    # Get transformation parameters from a particle
    def getTransf(self,name,*args,**opt):
        if name=='MainSink':
            return self.foreach(getTransf_MainSink,args=list(args),**opt)

    ######################################
    # Common plotting routines           #
    ######################################

    # Plot Arepo image
    def setImage(self, axis, prop, imgType, norm=None, normType=None, cmap=None):
        for item in self.items:
            if 'boxSize' not in item.sim.optImages:
                apy.shell.exit("No 'boxSize' option for simulation %d (groups.py)"%item.index)
            item.setTransf(box=item.sim.optImages['boxSize'])
        data = self.foreach(setImage,args=[prop,imgType])
        logNormsProps = ['density','rih','ndens']
        if not normType:
            normType = 'log' if prop in logNormsProps else 'lin'
        norm = 'img_%s_%s'%(prop,imgType) if norm is None else norm
        axis.setImage(data=data['im'],extent=data['extent'],norm=norm,normType=normType,cmap=cmap)

    # Add rendering of the box projection/slice
    def _renderImage(self, axis, prop, imgType, norm=None, normType=None, cmap=None, 
                     bins=200, cache=False, nproc=None, n_jobs=None, xnorm=True, ynorm=True):
        n_jobs = self.opt['n_jobs'] if n_jobs is None else n_jobs
        proj = self.foreach(renderImage,args=[imgType,prop,bins,n_jobs],
                            cache=cache, nproc=nproc)
        if isinstance(axis,list):
            for i in range(len(axis)):
                data = proj['data'][:,i]
                n = norm[i] if isinstance(norm,list) else norm
                nt = normType[i] if isinstance(normType,list) else normType
                c = cmap[i] if isinstance(cmap,list) else cmap
                axis[i].setImage(data=data, extent=proj['extent'], 
                                 norm=n, normType=nt, cmap=c, 
                                 xnorm=xnorm, ynorm=ynorm)
        else:
            axis.setImage(data=proj['data'],extent=proj['extent'], 
                          norm=norm, normType=normType, cmap=cmap, 
                          xnorm=xnorm, ynorm=ynorm)
    def setProjection(self, axis, prop, **opt):
        self._renderImage(axis, prop, 'proj', **opt)
    def setSlice(self, axis, prop, **opt):
        self._renderImage(axis, prop, 'slice', **opt)

    # Add times to the plot
    def addTimes(self, axis, **opt):
        values = self.foreach(addTimes)
        nopt = {'loc':'top left'}
        nopt.update(opt)
        axis.addText(values,**nopt)

    # Add redshift to the plot
    def addRedshifts(self, axis, **opt):
        values = self.foreach(addRedshifts)
        nopt = {'loc':'top left'}
        nopt.update(opt)
        axis.addText(values,**nopt)

    # Add snapshot number to the plot
    def addSnapNums(self, axis, **opt):
        values = self.foreach(addSnapNums)      
        nopt = {'loc':'top left'}
        nopt.update(opt)
        axis.addText(values,**nopt)    

    # Add particle scatter plot
    def addParticles(self, axis, ptype, **opt):
        coords = self.foreach(addParticles,append=True,args=[ptype])
        x,y=[],[]
        for coord in coords:
            x.append([] if coord is None else coord[:,0])
            y.append([] if coord is None else coord[:,1])
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
        data = self.foreach(addCoordSystem,args=[vector])
        for i in range(len(data['u'][0])):
            axis.addQuiver(0,0,data['u'][:,i],data['v'][:,i],color=colors[i],pivot='tail',angles='xy',
                           scale=1,scale_units='xy',alpha=data['alpha'][:,i])        
        if info:   # print information about rotations
            info = []
            for item in self.items:
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
    def addHistogram2D(self, axis, xprop, yprop, bins, norm=None, normType='lin',
                       xscale='lin', yscale='lin', cmap=None, aspect='auto'):
        if isinstance(bins,int): bins = [bins,bins]
        if isinstance(bins[0],int):
            xr = self.getPropertyRange(xprop, xscale)
            yr = self.getPropertyRange(yprop, yscale)
            bins[0] = np.linspace(xr[0],xr[1],bins[0]) if xscale=='lin' else np.logspace(xr[0],xr[1],bins[0])
            bins[1] = np.linspace(yr[0],yr[1],bins[1]) if yscale=='lin' else np.logspace(yr[0],yr[1],bins[1])
        allData = []
        pb = apy.shell.pb(vmax=self.size,label='Calculating histogram (%s,%s)'%(xprop,yprop))
        for item in self.items: 
            with item.getSnapshot() as sn:
                hist = sn.getProperty({'name':'Histogram2D',"x":xprop,'y':yprop,'bins':bins,'xscale':xscale,'yscale':yscale})
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

# Get transformation properties from the most massive sink particle
def getTransf_MainSink(item,lrad):
    snap = item.getSnapshot()
    pos, mass = snap.getProperty([
        {'name':'Coordinates','ptype':5},
        {'name':'Masses','ptype':5}
    ])
    ids = np.argmax(mass)
    center = pos[ids]         # select the most massive sink
    L = snap.getProperty({'name':'AngularMomentum','center':center,'radius':lrad})
    return {
        'center':center,
        'mass':mass[ids],
        'L':L,
    }

# Get sink properties
def getSinkProps(item,props,select):
    with item.getSink() as sn:
        pdata = sn.getValues(props,order='FormationOrder')
    ids = slice(len(pdata[0])) if select is None else np.in1d(pdata['ID'],select)
    data = {}
    for p,prop in enumerate(props):
        data[prop] = pdata[p][ids]
    return data

# Get snapshot number
def addSnapNums(item):
    return '%03d'%item.snap

# Get coordinate system vector projections
def addCoordSystem(item,vector):
    box = item.transf['crop']['box']
    size = np.min((box[1::2]-box[::2]) * 0.5 * item.sim.units.conv['length'])
    coord = [[size,0,0],[0,size,0],[0,0,size]]
    if 'align' in item.transf.items:   # show the alignment vector
        vector = item.transf.items['align']['vector']
        vector = vector/np.linalg.norm(vector)*size
        coord.append(vector)
    elif vector is not None:           # show arbitrary vector
        vector = vector[item.index] if np.ndim(vector)>1 else vector
        vector = vector/np.linalg.norm(vector)*size
        coord.append(vector)                
    u,v,w = item.transf.convert(['align','flip','rotate'],np.array(coord)).T
    return {
        'u':     u,
        'v':     v,
        'alpha': np.where(w<0,0.5,1.0)
    }
    
# Get snapshot redshifts
def addRedshifts(item):
    with item.getSnapshot() as sn:
        z = 1./sn.getHeader('Time')-1.
    return 'z = %.03f'%z

# Get snapshot times
def addTimes(item):
    with item.getSnapshot() as sn:
        time = item.sim.units.guess('time',sn.getHeader('Time'),utype='old')
    return 't = %s'%time

# Add particles
def addParticles(item,ptype):
    with item.getSnapshot() as sn:
        center = item.transf['select']['center']
        radius = item.transf['select']['radius']
        ids = sn.getProperty({'name':'RadialRegion','ptype':ptype,"center":center,'radius':radius})
        if len(ids)>0:
            coord = sn.getProperty({'name':'Coordinates','ptype':ptype},ids=ids)
            coord = item.transf.convert(['translate','align','flip','rotate','crop'],coord)
            return coord * item.sim.units.conv['length']
        else:
            return None
        
# Get arepo image
def setImage(item,prop,imgType):
    im,px,py = item.sim.getImage(item.snap,prop,imgType)
    if prop=='density':
        im *= item.sim.units.conv['density']
    box = item.transf['crop']['box']
    return {
        'im':     im,
        'box':    box,
        'extent': np.array(box[:4]) * item.sim.units.conv['length'],
        'center': (box[::2]+box[1::2])*0.5 * item.sim.units.conv['length'],
    }
    
# Get projection/slice of a region in the snapshot
def renderImage(item,rend,prop,bins,n_jobs):
    snap = item.getSnapshot()
    if rend=='proj':
        data = snap.getProperty({'name':'BoxProjection','transf':item.transf,'w':prop,'bins':bins,'n_jobs':n_jobs})
    elif rend=='slice':
        data = snap.getProperty({'name':'BoxSlice','transf':item.transf,'w':prop,'bins':bins,'n_jobs':n_jobs})
    return {
        'data':   data,
        'extent': item.transf['crop']['box'][:4] * item.sim.units.conv['length']
    }

#######################
# Overload item class #
#######################
class item(dataGroups.item):
    def __init__(self,index,groupName,opt,sim,snap):
        super().__init__(index,groupName,opt)
        self.sim = sim
        self.snap = snap

    # Set coordinate transformations
    def setTransf(self, **opt):
        self.transf = apy.coord.transf(**opt)   

    # snapshot file
    def getSnapshot(self,snap=None,**opt):
        if snap is None:
            snap = self.snap
        return self.sim.getSnapshot(snap,**opt)

    # sink file
    def getSink(self,snap=None,**opt):
        if snap is None:
            snap = self.snap
        return self.sim.getSink(snap,**opt)

    # image file
    def getImage(self,imProp,imType,snap=None,**opt):
        if snap is None:
            snap = self.snap
        return self.sim.getImage(snap,imProp,imType,**opt)
