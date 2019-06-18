import matplotlib as mpl; mpl.use('agg')
import matplotlib.pyplot as plt
import mpl_toolkits.axes_grid1 as axesgrid
import arepy as apy
import numpy as np

def plotSubplot(ax,opt,canvas,fid=0):
    fig = ax.figure

    def hideAxis(msg=''):
        if msg: apy.shell.printc(msg)
        ax.axis('off')
        return False
    
    # hide axis if it is not used
    if canvas['empty']:
        return hideAxis()
    
    axProp = canvas['axis']
    if 'xlim' in axProp: xlim = axProp['xlim'][fid] if np.ndim(axProp['xlim'])>1 else axProp['xlim']
    if 'ylim' in axProp: ylim = axProp['ylim'][fid] if np.ndim(axProp['ylim'])>1 else axProp['ylim']

    spIndex, spRow, spCol = canvas['subplot']

    fontsize = 8   # default font size
    twinx = None   # twin axis flag
    handles = []   # collector of plot handles
    for d in canvas['other']:
        if d['twinx'] and twinx==None:
            twinx = ax.twinx()
        drawax = twinx if d['twinx'] else ax

        # Draw a straight line
        if d['draw']=='line':
            pos = d['pos'] if np.isscalar(d['pos']) else d['pos'][fid]
            if d['axis']=='horizontal':
                li = drawax.axhline(pos,**d['kwargs'])
            elif d['axis']=='vertical':
                li = drawax.axvline(pos,**d['kwargs'])
            if 'label' in d['kwargs']:
                handles.append(li)
            
        # Draw x/y line continuous function
        if d['draw']=='plot':
            xvals = d['x'][fid] if np.ndim(d['x'])>1 else d['x']
            yvals = d['y'][fid] if np.ndim(d['y'])>1 else d['y']
            li = drawax.plot(xvals,yvals,**d['kwargs'])
            if 'label' in d['kwargs']:
                handles.append(li[0]) # for some reason this is a list of objects

        # Draw x/y line step function
        if d['draw']=='step':
            yvals = d['y'][fid] if np.array(d['y']).ndim>1 else d['y']
            li = drawax.step(d['x'],yvals,color=d['color'],ls=d['linestyle'],lw=1.,label=d['label'])
            if d['label']:
                handles.append(li[0]) # for some reason this is a list of objects

        # Draw x/y point scatter
        if d['draw']=='scatter':
            xvals = d['x'] if np.isscalar(d['x'][0]) else d['x'][fid]
            yvals = d['y'] if np.isscalar(d['y'][0]) else d['y'][fid]
            if d['z'] is None:
                li = drawax.scatter(xvals,yvals,**d['opt'])
            else:
                zvals = d['z'] if np.isscalar(d['z'][0]) else d['z'][fid]
                li = drawax.scatter(xvals,yvals,zvals,**d['opt'])
            if 'label' in d['opt']:
                handles.append(li)

        # Draw a quiver
        if d['draw']=='quiver':
            coord = []
            for c in d['coord']:
                coord.append( c if np.isscalar(c) else c[fid] )
            if 'alpha' in d['kwargs'] and not np.isscalar(d['kwargs']['alpha']):
                d['kwargs']['alpha'] = d['kwargs']['alpha'][fid]
            li = drawax.quiver(*coord,**d['kwargs'])
            if 'label' in d['kwargs']:
                handles.append(li)

        # Draw a bar plot
        if d['draw']=='bar':
            yvals = d['y'] if np.isscalar(d['y'][0]) else d['y'][fid]
            xvals = d['x'] if np.isscalar(d['x'][0]) else d['x'][fid]
            li = drawax.bar(xvals,yvals,tick_label=d['label'],color=d['color'])
            if d['labelrot'] is not None:
                for tick in drawax.get_xticklabels():
                    tick.set_rotation(d['labelrot'])

        # Draw a text field
        if d['draw']=='text':
            if not isinstance(d['loc'],str):
                x,y = d['loc']
            elif ('xlim' in axProp) and ('ylim' in axProp):
                x,y,ha,va = apy.util.calculateLoc(d['loc'],xlim,ylim,d['padding'])
            else:
                apy.shell.exit('Text location or plot axis limts were not set (plot.py)')
            text = d['text'] if isinstance(d['text'],str) else d['text'][fid]
            if d['bgcolor'] is not None:
                d['kwargs']['bbox'] = dict(boxstyle='square,pad=.1', fc=d['bgcolor'], ec='none')
            drawax.text(x, y, text, ha=ha, va=va, **d['kwargs'])

        # Draw a circle
        if d['draw']=='circle':
            shape = plt.Circle( d['center'], d['radius'], fill=False, **d['kwargs'])
            drawax.add_artist(shape)

        # Draw a rectangle
        if d['draw']=='rectangle':
            rect = mpl.patches.Rectangle(d['origin'],d['width'],d['height'],**d['kwargs'])
            drawax.add_patch(rect)
        
    # Draw a standard legend
    if canvas['legend'] is not None:
        legend = canvas['legend']
        if 'fontsize' not in legend['nopt']:
            legend['nopt']['fontsize'] = fontsize
        if (legend['handles'] is not None and legend['labels'] is not None):
            ax.legend(legend['handles'],legend['labels'],**legend['nopt'])
        elif legend['labels'] is not None:
            ax.legend(legend['labels'],**legend['nopt'])
        else:
            labels = [h.get_label() for h in handles]
            ax.legend(handles,labels,**legend['nopt'])

    # Draw a linestyle legend
    if canvas['legendLS'] is not None:
        legend = canvas['legendLS']
        if 'fontsize' not in legend['nopt']:
            legend['nopt']['fontsize'] = fontsize
        elements = []
        for i in range(len(legend['ls'])):
            elements.append( mpl.lines.Line2D([0], [0], color=legend['color'], ls=legend['ls'][i], lw=1 ) )
        leg = mpl.legend.Legend(ax, elements, legend['labels'], **legend['nopt'])
        ax.add_artist(leg);

    if canvas['image'] is not None:
        image = canvas['image']
        data = image['data'][fid] if len(np.array(image['data']).shape)>2 else image['data']
        if data!=[]:
            if image['normType']=='log':
                if image['norm'][1]<=0:
                    return hideAxis("\nWarning: Skipping image plots with zero/negative logarithmic norm!")
                norm = mpl.colors.LogNorm(vmin=image['norm'][1],vmax=image['norm'][2])
            elif image['normType'] in ['lin',None]:
                norm = mpl.colors.Normalize(vmin=image['norm'][0],vmax=image['norm'][2])
            extent = image['extent'][fid] if np.ndim(image['extent'])>1 else image['extent']
            im = ax.imshow( data.T, extent=extent, origin='lower', aspect=image['aspect'],
                            norm=norm, cmap=image['cmap'] )

    if canvas['colorbar'] is not None:
        #ax = mappable.axes
        colorbar = canvas['colorbar']
        orientation = 'horizontal' if colorbar['location']=='top' else 'vertical'
        divider = axesgrid.make_axes_locatable(ax)
        cax = divider.append_axes(colorbar['location'], size="5%", pad=0.05)
        if not im:
            apy.shell.exit('Colorbar cannot find any image')
        cbar = fig.colorbar(im, cax=cax, orientation=orientation)
        cbar.ax.tick_params(labelsize=fontsize)
        if colorbar['label'] is not None:
            cbar.set_label(colorbar['label'],fontsize=fontsize)
        if colorbar['location']=='top':
            cbar.ax.xaxis.set_label_position('top') 
            cbar.ax.xaxis.set_ticks_position('top') 

    if canvas['colorbarNA'] is not None:
        colorbar = canvas['colorbarNA']
        orientation = 'horizontal' if colorbar['location']=='top' else 'vertical'
        cbar_ax = fig.add_axes(colorbar['pos'])
        if not im:
            apy.shell.exit('Colorbar cannot find any image')
        cbar = fig.colorbar(im, cax=cbar_ax, orientation=orientation)
        cbar.ax.tick_params(labelsize=fontsize)
        if colorbar['label'] is not None:
            cbar.set_label(colorbar['label'])
        if colorbar['location']=='top':
            cbar.ax.xaxis.set_label_position('top') 
            cbar.ax.xaxis.set_ticks_position('top') 

    if axProp['xpos']=='top': 
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position("top")

    if axProp['ypos']=='right':
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position("right")

    # set labels
    if 'title' in axProp:
        ax.set_title( axProp['title'],   fontsize=fontsize )
    if 'xlabel' in axProp:
        ax.set_xlabel( axProp['xlabel'], fontsize=fontsize )
    if 'ylabel' in axProp:
        ax.set_ylabel( axProp['ylabel'], fontsize=fontsize )

    # group axis labels
    if 'group' in axProp:
        if 'title' in axProp['group'] and spRow>0:
            ax.set_title('')
        if 'xlabel' in axProp['group']:
            if (axProp['xpos']=='bottom' and spRow<opt['nrows']-1) or (axProp['xpos']=='top' and spRow>0):
                ax.set_xlabel('')
                #ax.set_xticklabels([])  # this does not work with gridspec
                plt.setp( ax.get_xticklabels(), visible=False)  # this works also with gridspec
        if 'ylabel' in axProp['group']:
            if (axProp['ypos']=='left' and spCol>0) or (axProp['ypos']=='right' and spCol<opt['ncols']-1):
                ax.set_ylabel('')
                #ax.set_yticklabels([])  # this does not work with gridspec
                plt.setp( ax.get_yticklabels(), visible=False)  # this works also with gridspec
                
    if 'xlim' in axProp:   ax.set_xlim( xlim )
    if 'ylim' in axProp:   ax.set_ylim( ylim )
    if 'xscale' in axProp and axProp['xscale'] in ['log','symlog']: ax.set_xscale( axProp['xscale'] )
    if 'yscale' in axProp and axProp['yscale'] in ['log','symlog']: ax.set_yscale( axProp['yscale'] )

    if 'xticklabels' in axProp and axProp['xticklabels'] is False: ax.set_xticklabels([])
    if 'yticklabels' in axProp and axProp['yticklabels'] is False: ax.set_yticklabels([])

    if 'xtickformat' in axProp:
        ax.xaxis.set_major_formatter(mpl.ticker.FormatStrFormatter(axProp['xtickformat']))
        ax.xaxis.set_minor_formatter(mpl.ticker.FormatStrFormatter(axProp['xtickformat']))

    # set twin axis properties
    if twinx is not None:
        if 'tlabel' in axProp: twinx.set_ylabel( axProp['tlabel'], fontsize=fontsize )
        if 'tlim'   in axProp: twinx.set_ylim( axProp['tlim'] )
        if 'tscale' in axProp and axProp['tscale'] in ['log','symlog']: twinx.set_yscale( axProp['tscale'] )

    # set same x and y ticks
    if 'xysame' in axProp:
        xticks = ax.axes.get_xticks()
        xlim = ax.get_xlim()
        xlabels = map(str,xticks)
        xticks = xticks[(xticks>xlim[0])&(xticks<xlim[1])] # some ticks may be outside of the limits
        ax.set_xlim( xlim ) 
        ax.set_ylim( xlim ) 
        ax.set_xticks( xticks )
        ax.set_yticks( xticks )

    # set additional tick parameters
    #ax.xaxis.set_tick_params(labelsize=fontsize)
    #ax.yaxis.set_tick_params(labelsize=fontsize)
    ax.tick_params(which='both', labelsize=fontsize)
    if 'tickparam' in axProp: ax.tick_params(**axProp['tickparam'])

def plotFigure(f,opt,canvas):

    if opt['axesgrid'] is not None:
        fig = plt.figure(figsize=opt['figSize'])
        grid = axesgrid.AxesGrid(fig, 111, **opt['axesgrid'])
        axs = []
        for r in range(opt['nrows']):
            for c in range(opt['ncols']):
                index = r*opt['ncols']+c
                axs.append( grid[index] )
                axis = canvas[index]['axis']
                if 'projection' in axis and axis['projection'] is not None:
                    apy.shell.exit('Projection needs to be implemented for the axesgrid (plot.py)')
    elif opt['gridspec'] is not None:
        # Create a figure using gridspec to get a tight layout
        fig = plt.figure(figsize=opt['figSize'])
        gs = mpl.gridspec.GridSpec(opt['nrows'], opt['ncols'], **opt['gridspec'])
        #if isinstance(opt['gridspec'],dict):
        #    gs.update(**opt['gridspec'])
        axs = []
        for r in range(opt['nrows']):
            for c in range(opt['ncols']):
                index = r*opt['ncols']+c
                axs.append( plt.subplot(gs[index]) )
                axis = canvas[index]['axis']
                if 'projection' in axis and axis['projection'] is not None:
                    apy.shell.exit('Projection needs to be implemented for the gridspec (plot.py)')
    else:
        # Create a figure and plot all subplots
        fig = plt.figure(figsize=opt['figSize'])
        axs = []
        for r in range(opt['nrows']):
            for c in range(opt['ncols']):
                index = r*opt['ncols']+c
                projection = canvas[index]['axis']['projection']
                axs.append( fig.add_subplot(opt['nrows'],opt['ncols'],index+1, projection=projection) )

    for canv in canvas:
        spIndex, spRows, spCols = canv['subplot']
        plotSubplot(axs[spIndex],opt,canv,f)
        
    if opt['gridspec'] is None and opt['axesgrid'] is None:
        plt.tight_layout()

    # Create a new directory and save the figure
    apy.shell.mkdir( opt['dirResults'], 'u')
    plt.savefig( opt['fileName']%f, bbox_inches='tight' )

    # Close figure
    plt.close(fig)

    
