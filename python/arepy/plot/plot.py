import matplotlib as mpl; mpl.use('agg')
import matplotlib.pyplot as plt
import mpl_toolkits.axes_grid1 as axesgrid
from mpl_toolkits.mplot3d import Axes3D
import arepy as apy
import numpy as np

####################################
# Compose a subplot
####################################

def plotSubplot(ax,opt,canvas,fid=0):
    fig = ax.figure

    def hideAxis(msg=''):
        if msg: apy.shell.printc(msg)
        ax.axis('off')
        return False        
    
    # hide axis if it is not used
    if canvas['empty']:
        return hideAxis()

    spIndex, spRow, spCol, spXYZ = canvas['subplot']
    
    axProp = canvas['axis']
    if 'lim' in axProp['xaxis']:
        xlim = axProp['xaxis']['lim'][fid] if np.ndim(axProp['xaxis']['lim'])>1 else axProp['xaxis']['lim']
    if 'lim' in axProp['yaxis']:
        ylim = axProp['yaxis']['lim'][fid] if np.ndim(axProp['yaxis']['lim'])>1 else axProp['yaxis']['lim']
    if spXYZ:
        if 'zlim' in axProp: zlim = axProp['zlim'][fid] if np.ndim(axProp['zlim'])>1 else axProp['zlim']

    ####################################
    # Drawing objects on the axes
    ####################################

    fontsize = 8   # default font size
    twiny = None   # twin axis flag (two y-axes)
    twinx = None   # twin axis flag (two x-axes)
    handles = []   # collector of plot handles
    images = []    # collector of image handles

    def draw_rectangle(ax,d):
        """ Draw a rectangle
        """
        xy     = d['xy']     if np.isscalar(d['xy'][0])  else d['xy'][fid]
        width  = d['width']  if np.isscalar(d['width'])  else d['width'][fid]
        height = d['height'] if np.isscalar(d['height']) else d['height'][fid]
        shape = mpl.patches.Rectangle(xy,width,height,**d['kwargs'])
        ax.add_patch(shape)
    
    def draw_plot(ax,d):
        """ Draw x/y line continuous function 
        """
        xvals = d['x'] if np.isscalar(d['x'][0]) else d['x'][fid]
        yvals = d['y'] if np.isscalar(d['y'][0]) else d['y'][fid]
        li = ax.plot(xvals,yvals,**d['kwargs'])
        if 'label' in d['kwargs']:
            handles.append(li[0]) # for some reason this is a list of objects

    def draw_text(ax,d):
        """Add text to the subplot
        
        :param str loc: Position of the text on the axes
        :param (float)*2 padding: Padding of the text from the border
        :param str bgcolor: Background color of the 'bbox' around the thext
        """
        if not isinstance(d['loc'],str):
            x,y,ha,va = d['loc']
        elif ('lim' in axProp['xaxis']) and ('lim' in axProp['yaxis']):
            x,y,ha,va = apy.util.calculateLoc(d['loc'],xlim,ylim,d['padding'],
                                              axProp['xaxis']['scale'],axProp['yaxis']['scale'])
        else:
            apy.shell.exit('Text location or plot axis limts were not set (plot.py)')
        text = d['text'] if isinstance(d['text'],str) else d['text'][fid]
        if d['bgcolor'] is not None:
            d['kwargs']['bbox'] = dict(boxstyle='square,pad=.1', fc=d['bgcolor'], ec='none')
        drawax.text(x, y, text, ha=ha, va=va, **d['kwargs'])

    for d in canvas['other']:
        if d['twiny'] and twiny==None:
            twiny = ax.twinx()
            drawax = twiny
        elif d['twinx'] and twinx==None:
            twinx = ax.twiny()
            drawax = twinx
        else:
            drawax = ax

        # Draw a straight line
        if d['draw']=='line':
            pos = d['pos'] if np.isscalar(d['pos']) else d['pos'][fid]
            if d['axis']=='horizontal':
                li = drawax.axhline(pos,**d['kwargs'])
            elif d['axis']=='vertical':
                li = drawax.axvline(pos,**d['kwargs'])
            if 'label' in d['kwargs']:
                handles.append(li)
            
        if d['draw']=='plot':
            draw_plot(drawax,d)
            
        # Draw x/y line step function
        if d['draw']=='step':
            xvals = d['x'] if np.isscalar(d['x'][0]) else d['x'][fid]
            yvals = d['y'] if np.isscalar(d['y'][0]) else d['y'][fid]
            li = drawax.plot(xvals,yvals, drawstyle='steps', **d['kwargs'])
            if 'label' in d['kwargs']:
                handles.append(li[0]) # for some reason this is a list of objects

        # Draw x/y point scatter
        if d['draw']=='scatter':
            if np.isscalar(d['x']): xvals=d['x']
            else: xvals = d['x'] if np.isscalar(d['x'][0]) else d['x'][fid]
            if np.isscalar(d['y']): yvals=d['y']
            else: yvals = d['y'] if np.isscalar(d['y'][0]) else d['y'][fid]
            dopt = d['opt'].copy() # this is necessary if we do not use parallel plotting
            if 'c' in dopt and not isinstance(dopt['c'],str):
                dopt['c'] = dopt['c'][fid]
            if spXYZ:
                if np.isscalar(d['z']): zvals=d['z']
                else: zvals = d['z'] if np.isscalar(d['z'][0]) else d['z'][fid]
                li = drawax.scatter(xvals,yvals,zvals,**dopt)
            else:
                li = drawax.scatter(xvals,yvals,**dopt)
            if 'label' in dopt:
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
            xvals = d['x'] if np.isscalar(d['x'][0]) else d['x'][fid]
            yvals = d['y'] if np.isscalar(d['y'][0]) else d['y'][fid]
            li = drawax.bar(xvals,yvals, **d['kwargs'])
            if 'label' in d['kwargs']:
                handles.append(li)
            #if d['labelrot'] is not None:
            #    for tick in drawax.get_xticklabels():
            #        tick.set_rotation(d['labelrot'])

        # Draw a text field
        if d['draw']=='text':
            draw_text(ax,d)

        # Draw a circle
        if d['draw']=='circle':
            rad    = d['radius'] if np.isscalar(d['radius'])    else d['radius'][fid]
            center = d['center'] if np.isscalar(d['center'][0]) else d['center'][fid]
            shape = plt.Circle( center, rad, **d['kwargs'])
            drawax.add_artist(shape)

        if d['draw']=='rectangle':
            draw_rectangle(drawax,d)

        # Draw an image
        if d['draw']=='image':
            data = d['data'][fid] if len(np.array(d['data']).shape)>2 else d['data']
            if data!=[]:
                if d['normType']=='log':
                    if d['norm'] is None:
                        apy.shell.printc("Warning: Skipping image with None norm!",'red')
                        return
                    elif d['norm'][1]<=0:
                        return hideAxis("\nWarning: Skipping image plots with zero/negative logarithmic norm!")
                    norm = mpl.colors.LogNorm(vmin=d['norm'][1],vmax=d['norm'][2])
                elif d['normType'] in ['lin',None]:
                    norm = mpl.colors.Normalize(vmin=d['norm'][0],vmax=d['norm'][2])
                else:
                    apy.shell.exit("Normalization type '%s' is not defined (plot.py)"%d['normType'])
                extent = d['extent'][fid] if np.ndim(d['extent'])>1 else d['extent']
                im = drawax.imshow( data.T, origin='lower', norm=norm, extent=extent, **d['kwargs'] )        
                images.append(im)

        # Draw a custom colorbar
        if d['draw']=='colorbarNA':
            orientation = 'horizontal' if d['location']=='top' else 'vertical'
            cbar_ax = fig.add_axes(d['pos'])
            if len(images)==0:
                apy.shell.exit('Colorbar cannot find any image')
            im = images[d['im']] if 'im' in d else images[0]
            cbar = fig.colorbar(im, cax=cbar_ax, orientation=orientation)
            if 'ticklabels' in d['xaxis']: cbar.ax.set_xticklabels(d['xaxis']['ticklabels'])
            if 'ticklabels' in d['yaxis']: cbar.ax.set_yticklabels(d['xaxis']['ticklabels'])
            if d['label'] is not None:
                cbar.set_label(d['label'],fontsize=fontsize)
            if d['location']=='top':
                cbar.ax.xaxis.set_label_position('top') 
                cbar.ax.xaxis.set_ticks_position('top') 
            cbar.ax.tick_params(labelsize=fontsize)

    ####################################
    # Colorbars
    ####################################

    if canvas['colorbar'] is not None:
        #ax = mappable.axes
        colorbar = canvas['colorbar']
        orientation = 'horizontal' if colorbar['location']=='top' else 'vertical'
        divider = axesgrid.make_axes_locatable(ax)
        cax = divider.append_axes(colorbar['location'], size="5%", pad=0.05)
        if len(images)==0:
            apy.shell.exit('Colorbar cannot find any image')
        im = images[colorbar['im']] if 'im' in colorbar else images[0]
        cbar = fig.colorbar(im, cax=cax, orientation=orientation)
        if colorbar['label'] is not None:
            cbar.set_label(colorbar['label'],fontsize=fontsize)
        if colorbar['location']=='top':
            cbar.ax.xaxis.set_label_position('top') 
            cbar.ax.xaxis.set_ticks_position('top') 
        cbar.ax.tick_params(labelsize=fontsize)

    ####################################
    # Legends
    ####################################

    # Draw a standard legend
    if canvas['legend'] is not None:
        legend = canvas['legend']
        if 'fontsize' not in legend['nopt']:
            legend['nopt']['fontsize'] = fontsize
        zorder = None
        if 'zorder' in legend['nopt']:
            zorder = legend['nopt']['zorder']
            del legend['nopt']['zorder']
        if (legend['handles'] is not None and legend['labels'] is not None):
            leg = ax.legend(legend['handles'],legend['labels'],**legend['nopt'])
        elif legend['labels'] is not None:
            leg = ax.legend(legend['labels'],**legend['nopt'])
        else:
            labels = [h.get_label() for h in handles]
            leg = ax.legend(handles,labels,**legend['nopt'])
        if zorder:
            leg.set_zorder(zorder)

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

    # Draw a marker legend
    if canvas['legendM'] is not None:
        legend = canvas['legendM']
        if 'fontsize' not in legend['nopt']:
            legend['nopt']['fontsize'] = fontsize
        elements = []
        for i in range(len(legend['markers'])):
            elements.append( mpl.lines.Line2D([], [], color='None', marker=legend['markers'][i], 
                                              linestyle='', markersize=5, markerfacecolor='None', 
                                              markeredgecolor=legend['color'] ) )
        leg = mpl.legend.Legend(ax, elements, legend['labels'], **legend['nopt'])
        ax.add_artist(leg);

    ####################################
    # Axes
    ####################################
    
    def setAxisX(ax,props):
        axis = ax.xaxis
        if 'label' in props: ax.set_xlabel( props['label'], fontsize=fontsize )
        if 'lim'   in props: ax.set_xlim( props['lim'] )
        if 'scale' in props and  props['scale'] in ['log','symlog']:
            ax.set_xscale( props['scale'] )
        if 'visible' in props:
            axis.set_visible( props['visible'] )
        if 'pos' in props and props['pos']=='top': 
            axis.tick_top()
            axis.set_label_position("top")
        if 'ticks' in props: ax.set_xticks( props['ticks'] )
        if 'ticklabels' in props:
            ax.set_xticklabels( [] if props['ticklabels']==False else props['ticklabels'] )
        if 'tickformat' in props:
            axis.set_major_formatter(mpl.ticker.FormatStrFormatter(props['tickformat']))
        if 'tickparams' in props:
            if 'labelrotation' in props['tickparams']:
                plt.setp(ax.get_xticklabels(), rotation=props['tickparams']['labelrotation'])
            if 'axis' not in props['tickparams']:
                props['tickparams']['axis'] = 'x'
            ax.tick_params(**props['tickparams'])
        plt.setp(ax.get_xticklabels(), fontsize=fontsize)

    def setAxisY(ax,props):
        axis = ax.yaxis
        if 'label' in props: ax.set_ylabel( props['label'], fontsize=fontsize )
        if 'lim'   in props: ax.set_ylim( props['lim'] )
        if 'scale' in props and  props['scale'] in ['log','symlog']:
            ax.set_yscale( props['scale'] )
        if 'visible' in props:
            axis.set_visible( props['visible'] )
        if 'pos' in props and props['pos']=='right': 
            axis.tick_right()
            axis.set_label_position("right")
        if 'ticks' in props: ax.set_yticks( props['ticks'] )
        if 'ticklabels' in props:
            ax.set_yticklabels( [] if props['ticklabels']==False else props['ticklabels'] )
        if 'tickformat' in props:
            axis.set_major_formatter(mpl.ticker.FormatStrFormatter(props['tickformat']))
        if 'tickparams' in props:
            if 'axis' not in props['tickparams']:
                props['tickparams']['axis'] = 'y'
            ax.tick_params(**props['tickparams'])
        plt.setp(ax.get_yticklabels(), fontsize=fontsize)

    # set same x and y ticks
    if 'xysame' in axProp:
        xticks = ax.axes.get_xticks()
        xlim = ax.get_xlim()
        xlabels = map(str,xticks)
        xticks = xticks[(xticks>xlim[0])&(xticks<xlim[1])] # some ticks may be outside of the limits
        axProp['xaxis']['lim'] = xlim
        axProp['yaxis']['lim'] = xlim
        axProp['xaxis']['ticks'] = xticks
        axProp['yaxis']['ticks'] = xticks

    # set twin x/y-axis properties
    setAxisX(ax,axProp['xaxis'])
    if twinx is not None:
        setAxisX(twinx,axProp['twinx'])

    setAxisY(ax,axProp['yaxis'])
    if twiny is not None:
        setAxisY(twiny,axProp['twiny'])
        
    # set labels
    if 'title' in axProp:
        ax.set_title( axProp['title'],   fontsize=fontsize )
    if 'zlabel' in axProp:
        ax.set_zlabel( axProp['zlabel'], fontsize=fontsize )

    # group axis labels
    if 'group' in axProp or 'groupdiag' in axProp:
        if ('group' in axProp):
            minRow, maxRow = 0, opt['nrows']-1
            minCol, maxCol = 0, opt['ncols']-1
            groupProp = axProp['group']
        if ('groupdiag' in axProp):
            minRow, maxRow = 0, opt['nrows']-spCol
            minCol, maxCol = 0, opt['ncols']-spRow
            groupProp = axProp['groupdiag']

        if 'title' in groupProp and spRow>0:
            ax.set_title('')
        if 'xlabel' in groupProp:
            if (axProp['xaxis']['pos']=='top' and spRow>minRow) or (axProp['xaxis']['pos']=='bottom' and spRow<maxRow):
                ax.set_xlabel('')
                #ax.set_xticklabels([])  # this does not work with gridspec
                plt.setp( ax.get_xticklabels(), visible=False)  # this works also with gridspec
        if 'ylabel' in groupProp:
            if (axProp['yaxis']['pos']=='left' and spCol>minCol) or (axProp['yaxis']['pos']=='right' and spCol<maxRow):
                ax.set_ylabel('')
                #ax.set_yticklabels([])  # this does not work with gridspec
                plt.setp( ax.get_yticklabels(), visible=False)  # this works also with gridspec
                
    if spXYZ and 'zlim' in axProp:   ax.set_zlim( zlim )
        
####################################
# Compose a figure
####################################

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

    elif opt['imagegrid'] is not None:
        fig = plt.figure(figsize=opt['figSize'])
        if 'nrows_ncols' not in opt['imagegrid']:
            opt['imagegrid']['nrows_ncols'] = (opt['nrows'], opt['ncols'])
        grid = axesgrid.ImageGrid(fig, 111, **opt['imagegrid'])
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
                if opt['merge'] and opt['merge'][0]==index:
                    ax = fig.add_subplot(gs[r,:])
                    axs.append( ax )
                elif opt['merge'] and opt['merge'][1]==index:
                    continue
                else:
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
                projection = '3d' if canvas[index]['subplot'][3] else None
                figure = fig.add_subplot(opt['nrows'],opt['ncols'],index+1, projection=projection)
                axs.append( figure )

    for canv in canvas:
        spIndex, spRows, spCols, spXYZ = canv['subplot']
        plotSubplot(axs[spIndex],opt,canv,f)
        
    if opt['gridspec'] is None and opt['axesgrid'] is None:
        plt.tight_layout()

    # Create a new directory and save the figure
    apy.shell.mkdir( opt['dirResults'], 'u')
    plt.savefig( opt['fileName']%f, bbox_inches='tight' )

    # Close figure
    plt.close(fig)

    
