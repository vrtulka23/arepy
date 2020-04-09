import arepy as apy
import numpy as np

class setup(apy.scripy.setup):
    def init(self):
        self.opt['nRes'] = 64

    def setupConfig(self,fileName,defValues):
        f = apy.files.config(self.dirSetup+'/Config.sh')
        f.setValue(defValues)
        f.write(fileName)

    def setupParam(self,fileName,defValues):
        f = apy.files.param(self.dirSetup+'/param.txt')
        f.setValue(defValues)
        f.write(fileName)

    def setupRun(self,fileName,defValues):
        f = apy.files.runsh()
        f.setValue(defValues)
        f.write(fileName)

    def setupSources(self,fileName):
        f = apy.files.sources()
        coord = [0.5,0.5,0.5]
        sed = [ 0.0, 0.0, 1e50, 0.0, 0.0 ]
        f.addSource(coord,sed)
        f.write(fileName)        

    def setupOlist(self,fileName):
        f = apy.files.olist()
        times = np.arange(0.05,0.65,0.05)
        f.setValue(times)
        f.write(fileName)

    def setupOther(self):
        apy.shell.cp('a.txt','b.txt')

    def setupIcs(self,fileName):
        opt = {
            'BoxSize': self.opt['boxSize'] 
        }
        with apy.files.ics(self.units,**opt) as f:
            if self.opt['meshrelax']:            
                f.useGrid(self.opt['icsRes'],self.opt['icsDens'])
            else:
                sim = self.proj.getSimulation(100)
                snap = sim.getSnapshot(0)
                f.setSnapshot(snap,self.opt['icsDens'])
            f.write(fileName)
