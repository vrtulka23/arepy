
# loc = "vertical horizontal"

def calculateLoc(loc,xlim,ylim,padding=None):
    if padding is None:
        padding = (0.01,0.01)
    hpad = (xlim[1]-xlim[0])*padding[0]
    vpad = (ylim[1]-ylim[0])*padding[1]

    loc = loc.split(' ')
    if 'left' in loc: 
        x=xlim[0] + hpad
        ha = 'left'
    elif 'right' in loc: 
        x=xlim[1] - hpad
        ha = 'right'
    else: 
        x=(xlim[1]+xlim[0])*0.5
        ha = 'center'

    if 'bottom' in loc:
        y=ylim[0] + vpad
        va = 'bottom'
    elif 'lower' in loc: 
        y=ylim[0] + vpad
        va = 'lower'
    elif 'top' in loc:
        y=ylim[1] - vpad
        va = 'top'
    elif 'upper' in loc: 
        y=ylim[1] - vpad
        va = 'upper'
    else: 
        y=(ylim[1]-ylim[0])*0.5
        va = 'center'

    return x,y,ha,va
