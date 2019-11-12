import time
class showLeap:
    """Time measuring function

    Args:
       name: name of a timer

    This class is mainly used to calculate the loading times of the imported modules and libraries.
    However, it can be used also in other parts of the code.
    """
    def __enter__(self):
        return self
    def __exit__(self, type, value, tb):
        self.end()
        return
    def __init__(self,name):
        print(name,end="")
        self.itime = time.time()
        self.stime = time.time()
        self.etime = 0
        self.details = False
    def show(self,name):
        """Show time of the particular timer

        Args:
           name: name of a timer
        """
        ntime = time.time()
        self.etime = ntime - self.stime
        self.stime = ntime
        if self.details: 
            print('\n  %-20s'%name, self.etime,end="")
    def end(self):
        """End the timer"""
        if self.details: 
            print('\nFinished',end="")
        print(' in %.3f s'%(time.time() - self.itime))        
