import time
import arepy as apy

class timer:
    def __init__(self):
        self.times = [time.time()]

    def leap(self,show=True,msg=None):
        if show: 
            msg = 'Leap %s in: '%msg if msg is not None else 'Leap %d in: '%len(self.times)
            self.show(-1,msg)
        self.times.append( time.time() )

    def get(self,leap=0):
        return self.times[leap]
        
    def end(self,show=True,msg=None):
        self.show(0,'Done in: ' if msg is None else msg)

    def show(self,leap,msg):
        step = time.time() - self.get(leap)
        timestr = apy.units('cgs').guess('time',step)
        apy.shell.printc('%s%s'%(msg,timestr))
