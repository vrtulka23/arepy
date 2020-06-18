import numpy as np

def strDec(num,force=False):
    dec = np.floor(np.log10(num))
    flt = num * 10**(-dec)
    if dec>-2 and dec<3 and force is False:
        return r"%.1f"%num
    else:
        return r"%.1f$\times10^{%d}$"%(flt,dec)
