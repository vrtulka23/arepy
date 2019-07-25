import arepy as apy 
import numpy as np

class {{namePlot}}(apy.scripy.plot):
    def init(self):
        self.opt['simOpt'] = {
            'initUnitsNew': {'length':apy.const.au},
            'initImages':True,
            'initSinks':True,
            'initSnap': True,
        }

#import arepy as apy
#import numpy as np
#from scripy.{{nameProject}}.plots.{{namePlot}} import {{namePlot}}
#
#class boxIonization({{namePlot}}):
#    def init(self):        
#        super().init()
#

        self.setProcessors( fig=38, kdt=1, snap=1 )
        self.setGroups(['names','sim','snaps'],[
            ( '103', 103, range(63,184) ),
            ( '104', 104, range(0,96) ),
            ( '105', 105, range(0,90) ),
            ( '106', 106, range(0,50) ),
        ])
        self.setFigure(2,self.grps.size,1,show=True)

    def plot(self):
        for grp in self.grps:
            sim = self.getSimulation(grp.opt['sim'],**self.opt['simOpt'])
            grp.addSnapshot(sim,grp.opt['snaps'])

            timeBegin = grp[0].getSnapshot().getHeader('Time')

            sdata = grp.foreach(getBoxIonization,cache=grp.name)

            sp = self.fig.getSubplot(0,grp.index,title='Box ionization',yscale='log',
                                xlabel='t (kyr)', ylabel='X_H+')
            sp.addPlot(sdata['time']-timeBegin,sdata['xhp'],ynorm='xhp')

            sp = self.fig.getSubplot(1,grp.index,xlabel='t (kyr)', ylabel='Number of sinks')
            sp.addPlot(sdata['time']-timeBegin,sdata['nsinks'],ynorm='num')

def getBoxIonization(item):
    snap = item.getSnapshot()
    time = snap.getHeader('Time')
    mass,mhp,mhep = snap.getProperty(['Masses','M_HP','M_HEP'])
    nsinks = snap.getHeader('NumPart_Total')[5]
    return {
        'time':   time, 
        'xhp':    mhp.sum()/mass.sum(), 
        'xhep':   mhep.sum()/mass.sum(), 
        'nsinks': nsinks
    }
