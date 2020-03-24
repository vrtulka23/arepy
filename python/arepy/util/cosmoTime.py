def cosmoTime(z1,z2=None):

    # Currently there is only Planck2015 cosmology available in astropy.
    # This setting should be actually added to the module in the file:
    # astropy/cosmology/parameters.py
    
    # Planck 2018 paper XII Table 2 final column (best fit)
    par = dict(
        Oc0=0.2607,
        Ob0=0.04897,
        Om0=0.311,
        H0=67.66,
        n=0.9665,
        sigma8=0.8102,
        tau=0.0561,
        z_reion=7.82,
        t0=13.787,
        Tcmb0=2.7255,
        Neff=3.046,
        flat=True,
        m_nu=[0., 0., 0.06],
        reference=("Planck Collaboration 2018, A&A, (Paper VI),"
                   " Table 2 (TT, TE, EE + lowE + lensing + BAO)")
    )

    from astropy.cosmology import FlatLambdaCDM
    from astropy import units as u

    Planck18 = FlatLambdaCDM(par['H0'], par['Om0'],
                             Tcmb0=par['Tcmb0'], Neff=par['Neff'],
                             m_nu=u.Quantity(par['m_nu'], u.eV), name='Planck18',
                             Ob0=par['Ob0'])

    time1 = Planck18.lookback_time(z1)
    if (z2==None):
        return time1
    else:
        time2 = Planck18.lookback_time(z2)
        return time1-time2
    
    '''
    from astropy.cosmology import Planck15

    time1 = Planck15.lookback_time(z1)
    if (z2==None):
        return time1
    else:
        time2 = Planck15.lookback_time(z2)
        return time1-time2
    '''
