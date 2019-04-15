import arepy as apy
import numpy as np

class dataset:
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        True

    def __init__(self, subplot, sim, snaps, **opt):

        # settings
        self.subplot = subplot
        self.snaps = [snaps] if isinstance(snaps,(int,float)) else snaps
        self.nSnaps = len(self.snaps)

        # set options
        self.opt = subplot.opt.copy()  
        self.opt.update(opt)

        # set unit conversion
        newUnits = self.opt['units'] if 'units' in self.opt else None
        if isinstance(sim,list):
            self.sim = sim
            for s in sim:
                s.initUnits({'new':newUnits})
                s.getImageBox()
        else:
            sim.initUnits({'new':newUnits})
            sim.getImageBox()
            self.sim = [sim]*self.nSnaps
 
        # other
        self.region = None

    def addTimeIonFront(self,props,thr,center,radius,bins=10,color=None,
                         linestyle='-',twinx=False,label=''):
        if isinstance(props,str):
            props, label = [props], [label]
        nProps = len(props)
        xdata = np.zeros((self.nSnaps))
        ydata = np.zeros((nProps,self.nSnaps))
        pb = apy.shell.pb(vmax=len(self.snaps),label='Reading %d snapshots'%self.nSnaps)
        for s,snap in enumerate(self.snaps):
            time = self.sim[s].getHeader('Time',snap)
            xdata[s] = time * self.sim[s].units.conv['time']
            ids, r = self.sim[s].getProperty('RadialRegion',snap,args={'center':center,'radius':radius[1]})            
            mass = self.sim[s].getProperty('Masses',snap,ids)
            abundnames=['xH2','xHP','xDP','xHD','xHEP','xHEPP','xH','xHE','xD']
            for p,prop in enumerate(props):
                if prop in abundnames:
                    abund = self.sim[s].getProperty(prop,snap,ids)
                    hmassab, edges = np.histogram(a=r,bins=bins,range=radius,weights=mass*abund,density=False)
                    hmass, edges = np.histogram(a=r,bins=bins,range=radius,weights=mass,density=False)
                    hist = hmassab/hmass
                    radii = (edges[1:]+edges[:-1])*0.5 * self.sim[s].units.conv['length']
                    rid = next(i for i,v in enumerate(hist) if v < thr)
                    ydata[p,s] = radii[rid]
            pb.increase()
        pb.close()

        norm = self.subplot.figure.norms.setNorm(ydata,'ylim')
        for p,prop in enumerate(props):
            self.subplot.draw.append({'draw':'plot','twinx':twinx,'x':xdata,'y':ydata[p],'label':label[p],
                                      'norm':norm,'color':color,'linestyle':linestyle})

    def addRadPropHist(self,props,center,radius,bins=10,color=None,
                       linestyle='-',twinx=False,label=''):
        if isinstance(props,str):
            props, label = [props], [label]
        nProps = len(props)
        data = np.zeros((nProps,self.nSnaps,bins))
        pb = apy.shell.pb(vmax=self.nSnaps,label='Reading %d snapshots (%s)'%(self.nSnaps,','.join(props)))
        for s,snap in enumerate(self.snaps):
            ids, r = self.sim[s].getProperty('RadialRegion',snap,args={'center':center,'radius':radius[1]})            
            abundnames=['xH2','xHP','xDP','xHD','xHEP','xHEPP','xH','xHE','xD']
            for p,prop in enumerate(props):
                if prop in abundnames:
                    mass, abund = self.sim[s].getProperty(['Masses',prop],snap,ids)
                    hmassab, edges = np.histogram(a=r,bins=bins,range=radius,weights=mass*abund,density=False)
                    hmass, edges = np.histogram(a=r,bins=bins,range=radius,weights=mass,density=False)
                    data[p,s,:] = hmassab/hmass
                    norm = self.subplot.figure.norms.setNorm(data[p,s,:],'ylim_abund')
                elif prop=='density':
                    mass = self.sim[s].getProperty('Masses',snap,ids)
                    hmass, edges = np.histogram(a=r,bins=bins,range=radius,weights=mass,density=False)
                    vols = 4./3.*np.pi*(edges[1:]**3-edges[:-1]**3)
                    data[p,s,:] = hmass/vols * self.sim[s].units.conv['density']
                    norm = self.subplot.figure.norms.setNorm(data[p,s,:],'ylim_density')
                elif prop=='temp':
                    mass, energy = self.sim[s].getProperty(['Masses','Temperature'],snap,ids)
                    hmassen, edges = np.histogram(a=r,bins=bins,range=radius,weights=mass*energy,density=False)
                    hmass, edges = np.histogram(a=r,bins=bins,range=radius,weights=mass,density=False)                    
                    data[p,s,:] = hmassen/hmass
                    norm = self.subplot.figure.norms.setNorm(data[p,s,:],'ylim_temp')
                else:
                    print( apy.shell.textc("Propery '%s' does not exist"%prop,'red') )
            pb.increase()
        pb.close()
        x = (edges[1:]+edges[:-1])*0.5 * self.sim[s].units.conv['length']
        for p,prop in enumerate(props):
            self.subplot.draw.append({'draw':'plot','twinx':twinx,'x':x,'y':data[p],'norm':norm,
                                      'color':color,'linestyle':linestyle,'label':label[p]})

    def addSnapSlice(self, prop, plane=None, bins=None, extent=None, norm=None, cmap=None):
        
        if plane==None:
            plane = self.sim[s].getParameter(['PicXmin','PicXmax','PicYmin','PicYmax','PicZmin'])            
        if bins==None:
            bins = self.sim[s].getParameter(['PicXpixels','PicYpixels'])

        allData = []
        pb = apy.shell.pb(vmax=self.nSnaps,label='Slicing %d snapshots (%s)'%(self.nSnaps,prop))
        for snap in self.snaps:
            ids, dist = self.sim[s].getProperty('SliceRegion',snap,args={'plane':plane,'bins':bins})
            data = self.sim[s].getProperty(prop,snap,ids)
            norm = self.subplot.figure.norms.setNorm(data,norm)
            allData.append( np.reshape(data,bins) )
            pb.increase()
        pb.close()

        if extent==None:
            xmin, xmax, ymin, ymax = plane[:4]
            xrad = (xmax - xmin) * 0.5
            yrad = (ymax - ymin) * 0.5
            extent = np.array([ -xrad, xrad, -yrad, yrad ]) * self.sim[s].units.conv['length']
        self.subplot.image = {'data':allData,'norm':norm,'extent':extent,'cmap':cmap,
                              'property':prop,'type':'slice'}
        self.subplot.xlim = extent[:2]
        self.subplot.ylim = extent[2:]

    # new stuff
    ###########
    
    def setImage(self, imgProperty, imgType, extent=None, norm=None, normType=None, cmap=None):
        allData = []
        pb = apy.shell.pb(vmax=self.nSnaps,label='Reading images (%s_%s)'%(imgProperty,imgType))
        for s,snap in enumerate(self.snaps):
            data,px,py = self.sim[s].getImage(snap,imgProperty,imgType)
            if imgProperty=='density':
                data = data * self.sim[s].units.conv['density']
            allData.append(data)
            pb.increase()
        pb.close()

        #NOTE: the extent has to be treated for each simulation separately
        #      for now we assume that the simulations have the same settings
        if extent==None:
            region = self.sim[s].imageBox
            extent = np.array(region[:4]) * self.sim[s].units.conv['length']
            center = (region[::2]+region[1::2])*0.5
            self.region = region
            self.subplot.addTransf('translate', origin=center*self.sim[s].units.conv['length'] )

        linNormsProps = ['density','rih']
        if not normType:
            normType = 'log' if imgProperty in linNormsProps else 'lin'
        norm = 'img_%s_%s'%(imgProperty,imgType) if norm is None else norm
        self.subplot.setImage(data=allData,extent=extent,norm=norm,normType=normType,cmap=cmap)
        self.subplot.setOption(xlim=extent[:2], ylim=extent[2:])

    def addParticles(self, ptype, **nkwargs):
        xData,yData = [], []
        pb = apy.shell.pb(vmax=self.nSnaps,label='Reading particles (%d)'%(ptype))
        for s,snap in enumerate(self.snaps):
            with self.sim[s].getSnapshot(snap) as sn:
                if self.region is not None:
                    ids, coord = sn.getProperty(ptype,'BoxRegion',args={"box":self.region})
                else:
                    coord = sn.getProperty(ptype,'Coordinates')
            xData.append(coord[:,0] * self.sim[s].units.conv['length'])
            yData.append(coord[:,1] * self.sim[s].units.conv['length'])
            pb.increase()
        pb.close()
        kwargs = {'s':20,'marker':'+','c':'black','edgecolors':None,'linewidths':1}
        kwargs.update(nkwargs)
        self.subplot.addScatter(xData,yData, **kwargs)

    def getPropertyRange(self, ptype, prop, scale='lin'):
        ranges = np.zeros((self.nSnaps,2))
        pb = apy.shell.pb(vmax=self.nSnaps,label='Calculating range (%s)'%(prop))
        for s,snap in enumerate(self.snaps):
            with self.sim[s].getSnapshot(snap) as sn:
                if scale=='lin':
                    res = sn.getProperty(ptype,['Minimum','Maximum'],args={'p':prop})
                    ranges[s,0] = res[0].min()
                    ranges[s,1] = res[1].max()
                elif scale=='log':
                    res = sn.getProperty(ptype,['MinPos','Maximum'],args={'p':prop})
                    ranges[s,0] = np.log10(res[0].min())
                    ranges[s,1] = np.log10(res[1].max())
            pb.increase()
        pb.close()
        return np.sum(ranges,axis=0)
        
    def addHistogram2D(self, ptype, xprop, yprop, bins, norm=None, normType='lin',
                       xscale='lin', yscale='lin', cmap=None, aspect='auto'):
        if isinstance(bins,int): bins = [bins,bins]
        if isinstance(bins[0],int):
            xr = self.getPropertyRange(ptype, xprop, xscale)
            yr = self.getPropertyRange(ptype, yprop, yscale)
            bins[0] = np.linspace(xr[0],xr[1],bins[0]) if xscale=='lin' else np.logspace(xr[0],xr[1],bins[0])
            bins[1] = np.linspace(yr[0],yr[1],bins[1]) if yscale=='lin' else np.logspace(yr[0],yr[1],bins[1])
        args = {"x":xprop,'y':yprop,'bins':bins,'xscale':xscale,'yscale':yscale}            
        allData = []
        pb = apy.shell.pb(vmax=self.nSnaps,label='Calculating histogram (%s,%s)'%(xprop,yprop))
        for s,snap in enumerate(self.snaps):
            with self.sim[s].getSnapshot(snap) as sn:
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
        self.subplot.setImage(data=allData,extent=extent,norm=norm,normType=normType,cmap=cmap,aspect=aspect)
        self.subplot.setOption(xlim=extent[:2], ylim=extent[2:])
        
    def addTimes(self,loc='top left'):
        times = []
        pb = apy.shell.pb(vmax=self.nSnaps,label='Reading times')
        for s,snap in enumerate(self.snaps):
            with self.sim[s].getSnapshot(snap) as sn:
                time = self.sim[s].units.guess('time',sn.getHeader('Time'),utype='old')
                times.append('t = %s'%time)
            pb.increase()
        pb.close()
        self.subplot.addText(times,loc)

    def addRedshifts(self,loc='top left'):
        redshifts = []
        pb = apy.shell.pb(vmax=self.nSnaps,label='Reading redshifts')
        for s,snap in enumerate(self.snaps):
            with self.sim[s].getSnapshot(snap) as sn:
                a = sn.getHeader('Time')
                z = 1./a-1.
                redshifts.append('z = %.02f'%z)
            pb.increase()
        pb.close()
        self.subplot.addText(redshifts,loc)

    def addSnapNums(self,loc='top right'):
        snaps = []
        for s,snap in enumerate(self.snaps):
            snaps.append('%03d'%snap)
        self.subplot.addText(snaps,loc)

    def setGridRegion(self, ptype, prop, bins, box, norm=None, cmap=None):
        grid, xi = apy.coord.grid(bins,box)

        allData = []
        pb = apy.shell.pb(vmax=self.nSnaps,label='Computing %d grid regions (%s)'%(self.nSnaps,prop))
        for s,snap in enumerate(self.snaps):
            with self.sim[s].getSnapshot(snap) as sn:
                ids, dist = sn.getProperty(ptype,'GridRegion',args={"grid":grid})
                coord, dens = sn.getProperty(ptype,['Coordinates',prop],ids=ids)
                data, xe, ye = np.histogram2d(grid[:,0],grid[:,1],bins=bins[:2],weights=dens)
            allData.append(data)
            pb.increase()
        pb.close()
        
        self.region = box
        extent = np.array(self.region[:4]) * self.sim[s].units.conv['length']
        center = (self.region[::2]+self.region[1::2])*0.5
        self.subplot.addTransf('translate', origin=center*self.sim[s].units.conv['length'] )
        
        logNormsProps = ['Density']
        normType = 'log' if prop in logNormsProps else 'lin'
        norm = 'grid_%s'%(prop) if norm is None else norm
        self.subplot.setImage(data=allData,extent=extent,norm=norm,normType=normType,cmap=cmap)
        self.subplot.setOption(xlim=extent[:2], ylim=extent[2:4])
            
