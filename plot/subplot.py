import numpy as np
import arepy as apy
import copy

class subplot:
    # Initialize the subplot
    def __init__(self, figure, row, col, **opt):
        self.figure = figure                  # parent figure class
        self.row = row                        # row on the grid
        self.col = col                        # column on the grid
        self.index = row*figure.nCols+col     # subplot index
        
        # set options
        self.opt = figure.opt.copy()  
        self.opt.update(opt)

        self.canvas = {
            'subplot': [self.index,self.row,self.col],      # subplot properties
            'empty': True,      # is canvas empty
            'image': None,      # main image on the figure
            'colorbar': None,   # colorbar of the image
            'colorbarG': None,  # group colorbar
            'legend': None,     # standard plot legend
            'legendLS': None,   # plot linestyle legend
            'other': [],        # other canvas objects
            'axis': {           # axis properties
                'xscale': 'lin',        # x axis scale
                'yscale': 'lin',        # y axis scale
                'tscale': 'lin',        # twin y axis scale
            },
        }
        self.xnorm = 'xnorm_%d'%self.index  # x-axis norm
        self.ynorm = 'ynorm_%d'%self.index  # y-axis norm
        self.znorm = 'znorm_%d'%self.index  # z-axis or image norm
        self.tnorm = 'tnorm_%d'%self.index  # twin y-axis norm
        
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
    def setLegend(self, handles=None, labels=None, loc='best', frameon=True, fontsize=8):
        self.canvas['legend'] = {'draw':'legend','handles':handles,'labels':labels,
                                 'loc':loc,'frameon':frameon,'fontsize':fontsize}

    # Example: sp.setLegendLS([':','--'],['foo','bar'])
    # Note: frameon=False
    def setLegendLS(self, linestyles, labels, loc='best', color='black', frameon=True, fontsize=8):
        self.canvas['legendLS'] = {'draw':'legendLS','ls':linestyles,'labels':labels,
                                   'loc':loc,'color':color,'frameon':frameon,'fontsize':fontsize}

    def setImage(self, data, extent=(0,1,0,1), norm=None, normType='lin', cmap=None, aspect='equal'):
        xextent = extent[:,:2] if np.ndim(extent)>1 else extent[:2]
        yextent = extent[:,2:] if np.ndim(extent)>1 else extent[2:]
        self.setNorm(xdata=xextent,ydata=yextent,zdata=data,zname=norm)        
        self.canvas['image'] = {'data':data,'norm':self.znorm,'normType':normType,
                                'extent':extent,'cmap':cmap,'aspect':aspect}

    def setColorbar(self, location='right', label=None):
        self.canvas['colorbar'] = {'location':location,'label':label}

    def setColorbarG(self, location='right', label=None):
        self.canvas['colorbarG'] = {'location':location,'label':label}
        
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

    def addScatter(self, x, y, xnorm=None, ynorm=None,**nopt):
        self.setNorm(xdata=x,ydata=y,xname=xnorm,yname=ynorm)
        opt = {'c': 'black'}
        opt.update(nopt)
        self.canvas['other'].append({'draw':'scatter','twinx':False,'x':x,'y':y,'kwargs':opt})

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
        
    def addCircle(self, center, radius, linestyle='-', color="white", twinx=False):        
        self.canvas['other'].append({'draw':'circle','twinx':twinx,'center':center,
                                     'radius':radius,'linestyle':linestyle,'color':color})
        
    def addText(self, text, loc, color='white', bgcolor='black', fontsize=8, twinx=False, padding=None ):
        self.canvas['other'].append({'draw':'text','twinx':twinx,'loc':loc,'text':text,
                                     'fontsize':fontsize,'color':color,'bgcolor':bgcolor,'padding':padding})

    # Read dataset and add its objects to the canvas
    def readDataset(self, sim, snaps):
        return apy.plot.dataset(self, sim, snaps)

    # Plot all canvas object on the given axis
    def getCanvas(self):

        # create a deep copy of the canvas
        canvas = copy.deepcopy(self.canvas)

        figs = range(self.figure.nFigs)

        # add all axis options
        axOpt = ['title','xlabel','ylabel','xlim','ylim','xscale','yscale',
                 'tlabel','tlim','tscale','group','xflip',
                 'xticklabels','yticklabels','xtickparam','ytickparam','tickparam','xysame']
        for opt in axOpt:
            if opt in self.opt:
                if self.opt[opt] is None: # remove if set to None
                    del self.opt[opt]
                    continue
                #if opt=='xlim':
                #    canvas['axis']['xlim'] = self.transf.convert(self.opt[opt],[0,0])
                #elif opt=='ylim':
                #    canvas['axis']['ylim'] = self.transf.convert(self.opt[opt],[1,1])
                #else:
                canvas['axis'][opt] = self.opt[opt]

        # transform x and y limits
        if 'xlim' not in canvas['axis'] and xnorm is not None:    
            xnorm = self.figure.norms.getLimits(self.xnorm)
            xnormmin = xnorm[1] if canvas['axis']['xscale']=='log' else xnorm[0]
            #canvas['axis']['xlim'] = self.transf.convert([xnormmin,xnorm[2]],0)
            canvas['axis']['xlim'] = [xnormmin,xnorm[2]]
        if 'ylim' not in canvas['axis'] and ynorm is not None:
            ynorm = self.figure.norms.getLimits(self.ynorm)
            ynormmin = ynorm[1] if canvas['axis']['yscale']=='log' else ynorm[0]
            #canvas['axis']['ylim'] = self.transf.convert([ynormmin,ynorm[2]],1)
            canvas['axis']['ylim'] = [ynormmin,ynorm[2]]

        # transform t limits
        if self.twinx:
            if 'tlim' not in canvas['axis'] and tnorm is not None:
                tnorm = self.figure.norms.getLimits(self.tnorm)
                tnormmin = tnorm[1] if canvas['axis']['tscale']=='log' else tnorm[0]
                #canvas['axis']['tlim'] = self.transf.convert([tnormmin,tnorm[2]],2)
                canvas['axis']['tlim'] = [tnormmin,tnorm[2]]

        # flip x axis
        if 'xflip' in canvas['axis'] and canvas['axis']['xflip']:
            canvas['axis']['xlim'] = [canvas['axis']['xlim'][:,1],canvas['axis']['xlim'][:,0]]
            
        # prepare unique objects
        if canvas['image'] is not None:
            image = canvas['image']
            canvas['image']['norm'] = self.figure.norms.getLimits(image['norm'])
            #canvas['image']['extent'] = self.transf.convert(image['extent'],[0,0,1,1])
            canvas['image']['extent'] = image['extent']
            
        # prepare multiple objects
        for i,d in enumerate(canvas['other']):
            if d['draw']=='text':
                if not isinstance(d['loc'],str):
                    #canvas['other'][i]['loc'] = self.transf.convert(d['loc'],[0,1])
                    canvas['other'][i]['loc'] = d['loc']
            if d['draw']=='scatter':
                #canvas['other'][i]['x'] = self.transf.convert(d['x'],0)
                #canvas['other'][i]['y'] = self.transf.convert(d['y'],1)
                canvas['other'][i]['x'] = d['x']
                canvas['other'][i]['y'] = d['y']
                
        return canvas
    
