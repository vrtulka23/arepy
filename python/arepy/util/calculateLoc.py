
# loc = "vertical horizontal"

def calculateLoc(loc,xlim,ylim,padding=None):
    if padding is None:
        padding = (0.01,0.01)
    hpad = (xlim[1]-xlim[0])*padding[0]
    vpad = (ylim[1]-ylim[0])*padding[1]
    va, ha = loc.split(' ')
    if ha=='left': x=xlim[0] + hpad
    if ha=='right': x=xlim[1] - hpad
    if ha=='center': x=(xlim[1]+xlim[0])*0.5
    if va in ['bottom','lower']: y=ylim[0] + vpad
    if va in ['top','upper']: y=ylim[1] - vpad
    if va=='center': y=(ylim[1]-ylim[0])*0.5
    return x,y,ha,va
