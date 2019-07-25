import numpy as np
import arepy as apy
import copy

class subplot:
    # Initialize the subplot
    def __init__(self, figure, row, col, **opt):
        self.figure = figure                  # parent figure class
        self.row = row                        # row on the grid
        self.col = col                        # column on the grid
        self.index = row*figure.ncols+col     # subplot index
        
        # set options and canvas
        self.opt = figure.opt.copy()  
        self.opt.update(opt)

        self.canvas = {
            'subplot': [self.index,self.row,self.col],      # subplot properties
            'empty': True,      # is canvas empty
            'image': None,      # main image on the figure
            'colorbar': None,   # colorbar of the image
            'colorbarNA': None, # colorbar on a new axis
            'legend': None,     # standard plot legend
            'legendLS': None,   # plot linestyle legend
            'other': [],        # other canvas objects
            'axis': {           # axis properties
                'xpos':   'bottom',     # x axis position
                'ypos':   'left',       # y axis position
                'xscale': 'lin',        # x axis scale
                'yscale': 'lin',        # y axis scale
                'tscale': 'lin',        # twin y axis scale
                'projection': None,     # 3d projection
            },
        }
        rc = '%d%d'%(self.row,self.col)
        self.xnorm = 'xnorm_'+rc  # x-axis norm
        self.ynorm = 'ynorm_'+rc  # y-axis norm
        self.znorm = 'znorm_'+rc  # z-axis or image norm
        self.tnorm = 'tnorm_'+rc  # twin y-axis norm
        
        self.twinx = False

    # Setting options
    def setOption(self,**args):
        for key,value in args.items():
            self.opt[key] = value

    # Standard way how to set a norm for the subplot
    def setNorm(self,xdata=None,ydata=None,zdata=None,
                xname=None,yname=None,zname=None,twinx=False):
        if xdata is not None:
            self.xnorm = self.figure.norms.setNorm(xdata,self.xnorm if xname is None else xname)
        if ydata is not None:
            if twinx:
                self.twinx = True
                self.tnorm = self.figure.norms.setNorm(ydata,self.tnorm if yname is None else yname)
            else:
                self.ynorm = self.figure.norms.setNorm(ydata,self.ynorm if yname is None else yname)        
        if zdata is not None:
            self.znorm = self.figure.norms.setNorm(zdata,self.znorm if zname is None else zname)
                    
    # Add unique objects to the canvas

    # Note: frameon=False
    def setLegend(self, handles=None, labels=None, **nopt):
        if 'loc' in nopt:
            nopt['loc'] = nopt['loc'].replace('bottom','lower').replace('top','upper')
        self.canvas['legend'] = {'draw':'legend','handles':handles,'labels':labels,'nopt':nopt}

    # Example: sp.setLegendLS([':','--'],['foo','bar'])
    # Note: frameon=False
    def setLegendLS(self, linestyles, labels, color='black', **nopt):
        if 'loc' in nopt:
            nopt['loc'] = nopt['loc'].replace('bottom','lower').replace('top','upper')
        self.canvas['legendLS'] = {'draw':'legendLS','ls':linestyles,'labels':labels,'color':color,'nopt':nopt}

    def setImage(self, data, extent=(0,1,0,1), norm=None, normType='lin', cmap=None, aspect='equal', xnorm=None, ynorm=None):
        xextent = extent[:,:2] if np.ndim(extent)>1 else extent[:2]
        yextent = extent[:,2:] if np.ndim(extent)>1 else extent[2:]
        self.setNorm(xdata=xextent,ydata=yextent,zdata=data,
                     xname=xnorm,yname=ynorm,zname=norm)        
        self.setOption(xlim=xextent, ylim=yextent)
        self.canvas['image'] = {'data':data,'norm':self.znorm,'normType':normType,
                                'extent':extent,'cmap':cmap,'aspect':aspect}

    def setColorbar(self, location='right', label=None):
        self.canvas['colorbar'] = {'location':location,'label':label}

    # colorbar on new axis
    def setColorbarNA(self, pos, **nopt):
        opt = {'location':'right'}
        opt.update(nopt)
        self.canvas['colorbarNA'] = {'pos':pos,**opt}
        
    def addPlot(self, x, y, twinx=False, xnorm=None, ynorm=None, **nopt):
        self.setNorm(xdata=x,ydata=y,xname=xnorm,yname=ynorm,twinx=twinx)
        opt = {'lw': 1}
        opt.update(nopt)
        self.canvas['other'].append({'draw':'plot','twinx':twinx,'x':x,'y':y,'kwargs':opt})

    def addStep(self, x, y, color=None, ls='-', twinx=False, label='', 
                xnorm=None, ynorm=None):
        self.setNorm(xdata=x,ydata=y,xname=xnorm,yname=ynorm,twinx=twinx)
        self.canvas['other'].append({'draw':'step','twinx':twinx,'x':x,'y':y,'label':label,
                                     'color':color,'linestyle':ls})

    def addScatter(self, *coord, xnorm=None, ynorm=None,**nopt):
        opt = {'c': 'black'}
        opt.update(nopt)
        self.setNorm(xdata=coord[0],ydata=coord[1],xname=xnorm,yname=ynorm)
        x,y,z = coord if self.opt['projection']=='3d' else (coord[0],coord[1],None)
        self.canvas['other'].append({'draw':'scatter','twinx':False,'x':x,'y':y,'z':z,'opt':opt})
        
    def addQuiver(self, *coord, **nopt):
        self.canvas['other'].append({'draw':'quiver','twinx':False,'coord':coord,'kwargs':nopt})

    def addBar(self, y, x=None, color=None, label='', labelrot=None, twinx=False):
        if x is None:
            x = np.arange(1,1+len(y))
            self.setNorm(xdata=[0,1+len(y)])
        self.canvas['other'].append({'draw':'bar','twinx':twinx,'x':x,'y':y,
                                     'color':color,'label':label,'labelrot':labelrot})

    def addLine(self, axis, pos, twinx=False, **nopt):
        opt = {'color':'grey', 'ls':'-', 'label':'', 'lw': 1}
        opt.update(nopt)
        self.canvas['other'].append({'draw':'line','twinx':twinx,'pos':pos,'axis':axis,'kwargs':opt})
        
    def addCircle(self, center, radius, twinx=False, **nopt):        
        opt = {'color':'black'}
        opt.update(nopt)
        self.canvas['other'].append({'draw':'circle','twinx':twinx,'center':center,
                                     'radius':radius,'kwargs':opt})
        
    def addText(self, text, loc, bgcolor=None, twinx=False, padding=None, **nopt):
        opt = {'color':'black', 'fontsize': 8}
        opt.update(nopt)
        self.canvas['other'].append({'draw':'text','twinx':twinx,'loc':loc,'text':text,
                                     'bgcolor':bgcolor,'padding':padding,'kwargs':opt})

    def addRectangle(self, origin, width, height, **nopt):
        opt = {'color':'grey'}
        opt.update(nopt)
        self.canvas['other'].append({'draw':'rectangle','twinx':False,'origin':origin,
                                     'width':width,'height':height,'kwargs':opt})

    # Read dataset and add its objects to the canvas
    def readDataset(self, sim, snaps):
        return apy.plot.dataset(self, sim, snaps)

    # Plot all canvas object on the given axis
    def getCanvas(self):

        # create a deep copy of the canvas
        canvas = copy.deepcopy(self.canvas)

        figs = range(self.figure.nfigs)

        # add all axis options
        axOpt = ['title','xlabel','ylabel','xlim','ylim','xscale','yscale',
                 'tlabel','tlim','tscale','group','xflip','xpos','ypos','projection',
                 'xticklabels','yticklabels','xtickparam','ytickparam','tickparam','xysame',
                 'xtickformat']
        for opt in axOpt:
            if opt in self.opt:
                if self.opt[opt] is None: # remove if set to None
                    del self.opt[opt]
                    continue
                canvas['axis'][opt] = self.opt[opt]

        # transform x and y limits
        xnorm = self.figure.norms.getLimits(self.xnorm)
        ynorm = self.figure.norms.getLimits(self.ynorm)
        if 'xlim' not in canvas['axis'] and xnorm is not None:    
            xnormmin = xnorm[1] if canvas['axis']['xscale']=='log' else xnorm[0]
            canvas['axis']['xlim'] = [xnormmin,xnorm[2]]
        if 'ylim' not in canvas['axis'] and ynorm is not None:
            ynormmin = ynorm[1] if canvas['axis']['yscale']=='log' else ynorm[0]
            canvas['axis']['ylim'] = [ynormmin,ynorm[2]]

        # transform t limits
        if self.twinx:
            tnorm = self.figure.norms.getLimits(self.tnorm)
            if 'tlim' not in canvas['axis'] and tnorm is not None:
                tnormmin = tnorm[1] if canvas['axis']['tscale']=='log' else tnorm[0]
                canvas['axis']['tlim'] = [tnormmin,tnorm[2]]

        # flip x axis
        if 'xflip' in canvas['axis'] and canvas['axis']['xflip']:
            canvas['axis']['xlim'] = [canvas['axis']['xlim'][:,1],canvas['axis']['xlim'][:,0]]
            
        # prepare unique objects
        if canvas['image'] is not None:
            image = canvas['image']
            canvas['image']['norm'] = self.figure.norms.getLimits(image['norm'])
            canvas['image']['extent'] = image['extent']
            
        # prepare multiple objects
        for i,d in enumerate(canvas['other']):
            if d['draw']=='text':
                if not isinstance(d['loc'],str):
                    canvas['other'][i]['loc'] = d['loc']
            if d['draw']=='scatter':
                canvas['other'][i]['x'] = d['x']
                canvas['other'][i]['y'] = d['y']
                
        return canvas
    