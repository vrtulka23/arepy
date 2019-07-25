from matplotlib.lines import Line2D

def customLegend(ax,colors,styles,labels,loc=0):
    nLines = len(colors)
    lines = [Line2D([0],[0],color=colors[i],lw=2,ls=styles[i]) for i in range(nLines)]        
    return ax.legend(lines,labels,loc=loc)
