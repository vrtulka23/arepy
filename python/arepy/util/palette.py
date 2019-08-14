import arepy as apy
import matplotlib.cm as cm

def palette(name,num,reverse=False):
    if num<2:
        apy.shell.exit("Pallet cannot be created for only one color")
    colors = [getattr(cm, name)(s/float(num-1)) for s in range(num)]
    if reverse:
        colors.reverse()
    return colors
