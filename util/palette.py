import arepy as apy
import matplotlib.cm as cm

def palette(name,num):
    if num<2:
        apy.shell.exit("Pallet cannot be created for only one color")
    return [getattr(cm, name)(s/float(num-1)) for s in range(num)]
