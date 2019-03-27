import arepy as apy
import numpy as np

class group:
    def __init__(self):
        self.sims = []
        self.nSims = 0

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        True

    def addSimulation(self, dirSim, **kwargs):
        self.sims.append( apy.files.simulation(dirSim,**kwargs) )
        self.nSims += 1

    # Interpolate snapshots according to their times
    def getCommonSnaps(self,bins=None):
        allSnaps, allTimes = [], []

        # read times for all snapshots
        trange = np.zeros((self.nSims,4))
        with apy.util.pb(vmax=self.nSims,label='Reading times...') as pb:
            for s,sim in enumerate(self.sims):
                snaps = sim.getSnapNums()
                times = np.array([sim.getSnapshot(snap).getHeader('Time') for snap in snaps])
                allSnaps.append( snaps )
                allTimes.append( times )
                trange[s,:3] = [ times.min(), times.max(), len(times) ]
                pb.increase()
        tmin, tmax = np.max(trange[:,0]), np.min(trange[:,1])

        # calculates maximum common number of snapshots for all sims
        if bins==None: 
            for s in range(self.nSims):
                trange[s,3] = ((tmin<=allTimes[s]) & (allTimes[s]<=tmax)).sum()
            bins = int(trange[:,3].min())
        times = np.linspace(tmin,tmax,bins)

        # find the most fitting snapshots for interpolated times
        snaps = np.zeros((self.nSims,bins))
        for s in range(self.nSims):
            snaps[s] = np.interp(times,allTimes[s],allSnaps[s])        

        return np.around(snaps).astype(int), times
            
