import matplotlib as mpl
mpl.use('agg')
import matplotlib.pyplot as plt
from matplotlib import colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
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
    spIndex, spRow, spCol = canvas['subplot']
    
    twinx = None
    handles = []   # collector of plot handles
    for d in canvas['other']:
        if d['twinx'] and twinx==None:
            twinx = ax.twinx()
        drawax = twinx if d['twinx'] else ax

        # Draw a straight line
        if d['draw']=='line':
            if d['axis']=='horizontal':
                li = drawax.axhline(d['pos'],**d['kwargs'])
            elif d['axis']=='vertical':
                li = drawax.axvline(d['pos'],**d['kwargs'])
            if 'label' in d['kwargs']:
                handles.append(li)
            
        # Draw x/y line continuous function
        if d['draw']=='plot':
            yvals = d['y'][fid] if np.array(d['y']).ndim>1 else d['y']
            li = drawax.plot(d['x'],yvals,**d['kwargs'])
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
            li = drawax.scatter(xvals,yvals,**d['kwargs'])
            if 'label' in d['kwargs']:
                handles.append(li)

        # Draw a quiver
        if d['draw']=='quiver':
            coord = []
            for c in d['coord']:
                coord.append( c if np.isscalar(c) else c[fid] )
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
                x,y,ha,va = apy.util.calculateLoc(d['loc'],axProp['xlim'][fid],axProp['ylim'][fid],d['padding'])
            else:
                apy.shell.exit('Text location or plot axis limts were not set (plot.py)')
            text = d['text'] if isinstance(d['text'],str) else d['text'][fid]
            if d['bgcolor'] is not None:
                d['kwargs']['bbox'] = dict(boxstyle='square,pad=.1', fc=d['bgcolor'], ec='none')
            drawax.text(x, y, text, ha=ha, va=va, **d['kwargs'])

        # Draw a circle
        if d['draw']=='circle':
            shape = plt.Circle( d['center'], d['radius'], linestyle=d['linestyle'],color=d['color'], fill=False)
            drawax.add_artist(shape)
        
    # Draw a standard legend
    if canvas['legend'] is not None:
        legend = canvas['legend']
        if (legend['handles'] is not None and legend['labels'] is not None):
            ax.legend(legend['handles'],legend['labels'],loc=legend['loc'],fontsize=8)
        elif legend['labels'] is not None:
            ax.legend(legend['labels'],loc=legend['loc'],fontsize=8)
        else:
            labels = [h.get_label() for h in handles]
            ax.legend(handles,labels,loc=legend['loc'],
                      fontsize=legend['fontsize'],frameon=legend['frameon'])

    # Draw a linestyle legend
    if canvas['legendLS'] is not None:
        legend = canvas['legendLS']
        elements = []
        for i in range(len(legend['ls'])):
            elements.append( Line2D([0], [0], color=legend['color'], ls=legend['ls'][i], lw=1 ) )
        leg = mpl.legend.Legend(ax, elements, legend['labels'], loc=legend['loc'], 
                                fontsize=legend['fontsize'],frameon=legend['frameon'])        
        ax.add_artist(leg);

    if canvas['image'] is not None:
        image = canvas['image']
        data = image['data'][fid] if len(np.array(image['data']).shape)>2 else image['data']
        if data!=[]:
            if image['normType']=='lin':
                norm = colors.Normalize(vmin=image['norm'][0],vmax=image['norm'][2])
            elif image['normType']=='log':
                if image['norm'][1]<=0:
                    return hideAxis("\nWarning: Skipping image plots with zero/negative logarithmic norm!")
                norm = colors.LogNorm(vmin=image['norm'][1],vmax=image['norm'][2])
            im = ax.imshow( data.T, extent=image['extent'][fid], origin='lower', aspect=image['aspect'],
                            norm=norm, cmap=image['cmap'] )

    if canvas['colorbar'] is not None:
        #ax = mappable.axes
        colorbar = canvas['colorbar']
        orientation = 'horizontal' if colorbar['location']=='top' else 'vertical'
        divider = make_axes_locatable(ax)
        cax = divider.append_axes(colorbar['location'], size="5%", pad=0.05)
        if not im:
            apy.shell.exit('Colorbar cannot find any image')
        cbar = fig.colorbar(im, cax=cax, orientation=orientation)
        cbar.ax.tick_params(labelsize=8)
        if colorbar['label'] is not None:
            cbar.set_label(colorbar['label'])
        if colorbar['location']=='top':
            cbar.ax.xaxis.set_label_position('top') 
            cbar.ax.xaxis.set_ticks_position('top') 

    if canvas['colorbarG'] is not None:
        colorbar = canvas['colorbarG']
        orientation = 'horizontal' if colorbar['location']=='top' else 'vertical'
        fig.subplots_adjust(right=0.9)
        cbar_ax = fig.add_axes([0.91, 0.15, 0.01, 0.7])
        if not im:
            apy.shell.exit('Colorbar cannot find any image')
        cbar = fig.colorbar(im, cax=cbar_ax, orientation=orientation)
        cbar.ax.tick_params(labelsize=8)
        if colorbar['label'] is not None:
            cbar.set_label(colorbar['label'])
        if colorbar['location']=='top':
            cbar.ax.xaxis.set_label_position('top') 
            cbar.ax.xaxis.set_ticks_position('top') 

    # set main axis properties
    if 'group' in axProp and 'title' in axProp['group'] and spRow>0:
        ax.set_title('')
    elif 'title' in axProp:
        ax.set_title( axProp['title'],   fontsize=8 )
        
    if 'group' in axProp and 'xlabel' in axProp['group'] and spRow<opt['nrows']-1:
        ax.set_xlabel('')
        ax.set_xticklabels([])
    elif 'xlabel' in axProp:
        ax.set_xlabel( axProp['xlabel'], fontsize=8 )
            
    if 'group' in axProp and 'ylabel' in axProp['group'] and spCol>0:
        ax.set_ylabel('')
        ax.set_yticklabels([])
    elif 'ylabel' in axProp:
        ax.set_ylabel( axProp['ylabel'], fontsize=8 )
            
    if 'xlim' in axProp:   ax.set_xlim( axProp['xlim'][fid] )
    if 'ylim' in axProp:   ax.set_ylim( axProp['ylim'][fid] )
    if 'xscale' in axProp and axProp['xscale']=='log': ax.set_xscale( axProp['xscale'] )
    if 'yscale' in axProp and axProp['yscale']=='log': ax.set_yscale( axProp['yscale'] )

    if 'xticklabels' in axProp and axProp['xticklabels'] is False: ax.set_xticklabels([])
    if 'yticklabels' in axProp and axProp['yticklabels'] is False: ax.set_yticklabels([])

    # set twin axis properties
    if twinx is not None:
        if 'tlabel' in axProp: twinx.set_ylabel( axProp['tlabel'], fontsize=8 )
        if 'tlim'   in axProp: twinx.set_ylim( axProp['tlim'] )
        if 'tscale' in axProp and axProp['tscale']=='log': twinx.set_yscale( axProp['tscale'] )

    ax.xaxis.set_tick_params(labelsize=8)
    ax.yaxis.set_tick_params(labelsize=8)

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
    if 'tickparam' in axProp: ax.tick_params(**axProp['tickparam'])

def plotFigure(f,opt,canvas):

    if opt['gridspec'] is None:
        # Create a figure and plot all subplots
        fig = plt.figure(figsize=opt['figSize'])
        axs = []
        for r in range(opt['nrows']):
            for c in range(opt['ncols']):
                axs.append( fig.add_subplot(opt['nrows'],opt['ncols'],r*opt['ncols']+c+1) )
    else:
        # Create a figure using gridspec to get a tight layout
        fig = plt.figure(figsize=opt['figSize'])
        gs = gridspec.GridSpec(opt['nrows'], opt['ncols'])
        gs.update(wspace=opt['gridspec']['wspace'],hspace=opt['gridspec']['hspace'])
        axs = [plt.subplot(gs[i]) for i in range(opt['nrows']*opt['ncols'])]

    for canv in canvas:
        spIndex, spRows, spCols = canv['subplot']
        plotSubplot(axs[spIndex],opt,canv,f)
        
    if opt['gridspec'] is None:
        plt.tight_layout()

    # Create a new directory and save the figure
    apy.shell.mkdir( opt['dirResults'], 'u')
    plt.savefig( opt['fileName']%f, bbox_inches='tight' )

    # Close figure
    plt.close(fig)
