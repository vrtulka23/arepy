def cosmoTime(z1,z2=None):
    from astropy.cosmology import Planck15

    time1 = Planck15.lookback_time(z1)
    if (z2==None):
        return time1
    else:
        time2 = Planck15.lookback_time(z2)
        return time1-time2
