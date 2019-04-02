import arepy as apy 
import numpy as np

class plot(apy.scripy.plot):
    def init(self):
        self.opt['simOpt'] = {
            'initUnitsNew': {'length':apy.const.au},
            'initImages':True,
            'initSinks':True,
        }

class plotBoxIonization(plot):
    def init(self):        
        super().init()
        self.setGroups(['names','sim','snaps'],[
            ( '103', 103, range(63,184) ),
            ( '104', 104, range(0,96) ),
            ( '105', 105, range(0,90) ),
            ( '106', 106, range(0,50) ),
        ])
        self.setFigure(2,self.grps.size,1,debug=True,show=True)

    def plot(self):
        def getBoxIonization(item):
            snap = item.getSnapshot()
            time = snap.getHeader('Time')
            mass,mhp,mhep = snap.getProperty(['Masses','M_HP','M_HEP'])
            nsinks = snap.getHeader('NumPart_Total')[5]
            return time, mhp.sum()/mass.sum(), mhep.sum()/mass.sum(), nsinks

        for grp in self.grps.items():
            sim = self.proj.getSimulation(grp.opt['sim'],**self.opt['simOpt'])
            grp.addSnapshot(sim,grp.opt['snaps'])

            timeBegin = grp[0].getSnapshot().getHeader('Time')

            sp = self.fig.getSubplot(0,grp.index,title='Box ionization',yscale='log',
                                xlabel='t (kyr)', ylabel='X_H+')
            sdata = grp.foreach(getBoxIonization,['time','xhp','xhep','nsinks'],cache=True)
            sp.addPlot(sdata['time']-timeBegin,sdata['xhp'],ynorm='xhp')

            sp = self.fig.getSubplot(1,grp.index,xlabel='t (kyr)', ylabel='Number of sinks')
            sp.addPlot(sdata['time']-timeBegin,sdata['nsinks'],ynorm='num')
