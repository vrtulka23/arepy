import time
import arepy as apy

class timer:
    def __init__(self):
        self.times = [time.time()]

    def leap(self,show=True):
        if show: 
            self.show(-1,'Leap %d in: '%len(self.times))
        self.times.append( time.time() )

    def get(self,leap=0):
        return self.times[leap]
        
    def end(self,show=True):
        self.show(0,'Done in: ')

    def show(self,leap,msg):
        step = time.time() - self.get(leap)
        timestr = apy.units('cgs').guess('time',step)
        apy.shell.printc('%s%s'%(msg,timestr))
