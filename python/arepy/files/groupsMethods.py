import arepy as apy
import numpy as np
from arepy.files.groupsTransf import *

#################################
# Common data reduction methods #
#################################

class groupsMethods:
    """Group methods class
    """

    ##################################
    # Common transformation routines #
    ##################################
        
    def setTransf(self,**opt):
        """Set coordinate transformations for every item

        Example::
            
            center = [0.15,0.15,0.15]
            region = apy.coord.regionBox(center,0.2)
            grp.setTransf(region=region, origin=center)
        """
        for item in self.items:
            nopt = {}
            for k,v in opt.items():
                if k in ['region']:
                    nopt[k] = v[item.index] if isinstance(v,list) else v
                else:
                    nopt[k] = v[item.index] if np.ndim(v)>1 else v
            item.setTransf(**nopt)

    def getTransf(self,args,**opt):        
        """Get transformation parameters from a particle
        
        :param args: Settings of a transformation
        :param opt: Settings of the :meth:`arepy.data.group.foreach`

        Transformations are calculated in :class:`arepy.files.groups.groupsTransf`.
        """
        return self.foreach(getTransf,args=[args],**opt)

    def useTransf(self,transf,use=True,add={}):
        """Use transformation values
        """
        opt = {}
        if isinstance(use,list):
            for key in use:
                opt[key] = transf[key]
        else:
            for key in list(transf.keys()):
                opt[key] = transf[key]
        for key,val in add.items():
            opt[key] = val
        self.setTransf(**opt)

    ##################################
    # Commont snapshot analysis      #
    ##################################

    def getPropertyRange(self, prop, scale='lin'):
        """Calculate a range of properties
        """
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

    def getSinkProps(self,props,select=None,cache=None,update=True):
        """Create a list of sink particles with their properties in each snapshot
        """
        # get properties
        props = [props] if isinstance(props,str) else props
        if 'FormationOrder' not in props: props.append('FormationOrder')
        if 'ID' not in props:             props.append('ID')
        pdata = self.foreach(getSinkProps,args=[props,select],append=True,
                             cache=cache,update=update)
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

    ######################################
    # Common plotting routines           #
    ######################################

    # Plot Arepo image
    def setImage(self, sp, prop, imgType, norm=None, normType=None, cmap=None, multiply=None):
        """Set Arepo image
        """
        for item in self.items:
            if 'boxSize' not in item.sim.optImages:
                apy.shell.exit("No 'boxSize' option for simulation %d (groups.py)"%item.index)
            region = apy.coord.regionBox(item.sim.optImages['boxSize'])
            item.setTransf(region=region,origin=region.center)
        data = self.foreach(setImage,args=[prop,imgType])
        logNormsProps = ['density','rih','ndens']
        if not normType:
            normType = 'log' if prop in logNormsProps else 'lin'
        norm = 'img_%s_%s'%(prop,imgType) if norm is None else norm
        if multiply is not None: 
            data['im'] *= multiply
        sp.setImage(data=data['im'],extent=data['extent'],norm=norm,normType=normType,cmap=cmap)

    # Add rendering of the box projection/slice
    def _renderImage(self, sp, prop, imgType, 
                     bins=200, cache=False, nproc=None, n_jobs=None, **imgopt):
        #             norm=None, normType=None,  cmap=None, 
        #             xnorm=None, ynorm=None, aspect='equal'):
        n_jobs = self.opt['n_jobs'] if n_jobs is None else n_jobs
        prop = apy.files.properties(prop)
        proj = self.foreach(renderImage,args=[imgType,prop,bins,n_jobs],
                            cache=cache, nproc=nproc)
        if isinstance(sp,list):
            for i in range(len(sp)):
                data = proj[prop[i]['name']]
                newimgopt = imgopt.copy()
                newimgopt['norm']     = imgopt['norm'][i]     if isinstance(imgopt['norm'],list)     else imgopt['norm']
                newimgopt['normType'] = imgopt['normType'][i] if isinstance(imgopt['normType'],list) else imgopt['normType']
                if 'cmap' in imgopt:
                    newimgopt['cmap']     = imgopt['cmap'][i]     if isinstance(imgopt['cmap'],list)     else imgopt['cmap']
                sp[i].setImage(data=data, extent=proj['extent'], **newimgopt)
        else:
            sp.setImage(data=proj['data'],extent=proj['extent'], **imgopt)
    def setProjection(self, sp, prop, **opt):
        """Create a projection image of a snapshot property

        :param sp: Subplot of a figure
        :type sp: :class:`arepy.plot.subplot`
        :param str prop: A snapshot property
        :param int bins: Number of pixels (bins) per dimension
        :param bool cache: Name of the results cache
        :param int nproc: Number of processors per projection
        :param int n_jobs: Number of processors per KDTree
        
        Parameter 'imgopt' is a dictionary of options that are passed to :meth:`arepy.plot.subplot.setImage`, 
        together with the image 'data' and 'extent'.
        """
        self._renderImage(sp, prop, 'BoxProjCube', **opt)
    def setSlice(self, sp, prop, **opt):
        """Create a slice image of a snapshot property

        :param sp: Subplot of a figure
        :type sp: :class:`arepy.plot.subplot`
        :param str prop: A snapshot property
        :param int bins: Number of pixels (bins) per dimension
        :param bool cache: Name of the results cache
        :param int nproc: Number of processors per projection
        :param int n_jobs: Number of processors per KDTree
        
        Parameter 'imgopt' is a dictionary of options that are passed to :meth:`arepy.plot.subplot.setImage`, 
        together with the image 'data' and 'extent'.
        """
        self._renderImage(sp, prop, 'BoxSquareXY', **opt)

    # Add rendering of the box slice field
    def _renderField(self, sp, prop, bins=200, cache=False, nproc=None, n_jobs=None, xnorm=None, ynorm=None):
        n_jobs = self.opt['n_jobs'] if n_jobs is None else n_jobs
        prop = apy.files.properties(prop)
        prop.add('Coordinates')
        proj = self.foreach(renderImage,args=['BoxFieldXY',prop,bins,n_jobs],
                            cache=cache, nproc=nproc)
        field = proj[prop[0]['name']]
        coord = proj['Coordinates']
        sp.addQuiver(coord[:,:,0], coord[:,:,1], field[:,:,0], field[:,:,1])
        #if isinstance(sp,list):
        #    for i in range(len(sp)):
        #        data = proj[prop[i]['name']]
        #        sp[i].addQuiver(data=data, extent=proj['extent'], 
        #                          xnorm=xnorm, ynorm=ynorm)
        #else:
        #    sp.addQuiver(data=proj['data'],extent=proj['extent'], 
        #                  xnorm=xnorm, ynorm=ynorm)
    def setField(self, sp, prop, **opt):
        """Set a quiver field map on the image
        
        This function is used to display a vector field on the top of an image.
        """
        self._renderField(sp, prop, **opt)

    def setSnapStamp(self, sp, *args, **kwargs):
        """Show snapshot number in plots
        """
        text = self.foreach(setSnapStamp)
        sp.addText(text,*args,**kwargs)

    def addTimes(self, sp, **opt):
        """Show snapshot time in plots
        """
        values = self.foreach(addTimes)
        nopt = {'loc':'top left'}
        nopt.update(opt)
        sp.addText(values,**nopt)

    def addRedshifts(self, sp, **opt):
        """Show snapshot redshifts in plots
        """
        values = self.foreach(addRedshifts)
        nopt = {'loc':'top left'}
        nopt.update(opt)
        sp.addText(values,**nopt)

    def addSnapNums(self, sp, **opt):
        """Show snapshot numbers in plots
        """
        values = self.foreach(addSnapNums)      
        nopt = {'loc':'top left'}
        nopt.update(opt)
        sp.addText(values,**nopt)    

    def addParticles(self, sp, ptype, **opt):
        """Show particle location on the image
        """
        coords = self.foreach(addParticles,append=True,args=[ptype])
        x,y=[],[]
        for coord in coords:
            x.append([] if coord is None else coord[:,0])
            y.append([] if coord is None else coord[:,1])
        nopt = {'s':20,'marker':'+','c':'black','edgecolors':None,'linewidths':1}
        nopt.update(opt)
        if isinstance(sp,list):
            for i in range(len(sp)):
                sp[i].addScatter(x,y,**nopt)
        else:
            sp.addScatter(x,y,**nopt)

    def addCoordSystem(self, sp, info=False, vector=None):
        """Show coordinate system on the plot
        """
        colors = ['red','blue','gold','black']
        data = self.foreach(addCoordSystem,args=[vector])
        for i in range(len(data['u'][0])):
            sp.addQuiver(0,0,data['u'][:,i],data['v'][:,i],color=colors[i],pivot='tail',angles='xy',
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
            sp.addText(info,loc='bottom right',fontsize=6)

    def addHist2D(self, sp, xprop, yprop, bins, norm=None, normType='lin',
                       xscale='lin', yscale='lin', cmap=None, aspect='auto'):
        """Create a 2D property histogram
        """
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
                hist = sn.getProperty({'name':'Hist2D',"x":xprop,'y':yprop,'bins':bins,'xscale':xscale,'yscale':yscale})
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

# Get a transformation by name
def getTransf(item,args):
    with groupsTransf(item) as tr:
        return tr.getTransf(args)

# Get sink properties
def getSinkProps(item,props,select):
    with item.getSink() as sn:
        pdata = sn.getValues(props,order='FormationOrder',dictionary=True)        
    if select is not None:
        ids = np.in1d(pdata['ID'],select)
        for key in list(pdata.keys()):
            pdata[key] = pdata[key][ids]
    return pdata

# Get snapshot number
def addSnapNums(item):
    return '%03d'%item.snap

# Get coordinate system vector projections
def addCoordSystem(item,vector):
    box = item.transf['crop']['region'].limits
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
        center = item.transf['select']['region'].center
        radius = item.transf['select']['region'].radius
        ids = sn.getProperty({'name':'RegionSphere','ptype':ptype,"center":center,'radius':radius})
        if len(ids)>0:
            coord = sn.getProperty({'name':'Coordinates','ptype':ptype},ids=ids)
            coord = item.transf.convert(['translate','align','flip','rotate','crop'],coord)
            return coord * item.sim.units.conv['length']
        else:
            return None

# Create snapshot stamps
def setSnapStamp(item):
    return '%s/%03d'%(item.sim.name,item.snap)
        
# Get arepo image
def setImage(item,prop,imgType):
    im,px,py = item.sim.getImage(item.snap,prop,imgType)
    if prop=='density':
        im *= item.sim.units.conv['density']
    box = item.transf['crop']['region'].limits
    return {
        'im':     im,
        'box':    box,
        'extent': np.array(box[:4]) * item.sim.units.conv['length'],
        'center': (box[::2]+box[1::2])*0.5 * item.sim.units.conv['length'],
    }
    
# Get projection/slice of a region in the snapshot
def renderImage(item,imgType,prop,bins,n_jobs):
    snap = item.getSnapshot()
    if item.transf is None:
        apy.shell.exit('Picture rendering needs a transformation (groups.py)')
    data = snap.getProperty({'name':imgType,'transf':item.transf,'p':prop,'bins':bins,'n_jobs':n_jobs})
    if len(prop)==1:
        data = {'data': data}
    if 'Coordinates' in data:
        data['Coordinates'] = np.array(data['Coordinates']) * item.sim.units.conv['length']
    if 'Density' in data:
        data['Density'] = data['Density'][:] * item.sim.units.conv['density']
    data['extent'] = item.transf['crop']['region'].limits[:4] * item.sim.units.conv['length']
    return data
