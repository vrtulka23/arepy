import arepy as apy
import matplotlib.cm as cm

def palette(name,num):
    if name=='jet':
        palette = [cm.jet(s/float(num-1)) for s in range(num)]
    elif name=='viridis':
        palette = [cm.viridis(s/float(num-1)) for s in range(num)]
    elif name=='inferno':
        palette = [cm.inferno(s/float(num-1)) for s in range(num)]
    else:
        apy.shell.exit("No colormap called 'name' is implemented!")
    return palette
