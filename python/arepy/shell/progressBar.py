# Progress bar
# Example:
# 
# pb = progressBar(vmax=30, label="")
# ...pb.increase()
# pb.close()
#
# with progressBar(vmax=30, label="Progress:") as pb:
#     ...pb.increase()

import sys
import arepy as apy

class progressBar:
    def __init__(self, vmax=100, label="", nparts=80, draw=True):
        if vmax<=0:
            apy.shell.exit('vmax=%d has to be higher than zero  (progressBar.py)'%(vmax))

        self.pbar = ""
        self.pbarOld = ""
        self.label = label if label=="" else label+" "

        self.vcurrent = 0 
        self.vmax = vmax

        self.nparts = nparts
        self.setAmount(0)
        if draw: self.draw()

    def __str__(self):
        return str(self.pbar)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        
    def setAmount(self, vcurrent = 0):
        # enforce values to be within the interval
        if vcurrent < 0: vcurrent = 0
        if vcurrent > self.vmax: vcurrent = self.vmax
        self.vcurrent = vcurrent

        # calculate progress
        donePercent = int(round( (float(self.vcurrent) / float(self.vmax)) * 100.0 ))
        doneParts = int((donePercent / 100.0) * self.nparts)

        # prepare text for the console
        pbartext = "%"+str(len(str(self.vmax)))+"d/%d %3s%%"
        pbartext = pbartext%(self.vcurrent,self.vmax,str(donePercent))
        pbartext = self.label+' '*(self.nparts-len(self.label)-len(pbartext))+pbartext
        if doneParts<self.nparts:
            pbartext = '\033[7m'+pbartext[:doneParts] +'\033[27m'+ pbartext[doneParts:]
        self.pbar = apy.shell.textc(pbartext,'yellow')
        
    def setPercentage(self,newPercentage,draw=True):
        self.setAmount((newPercentage * float(self.vmax)) / 100.0)
        if (draw): self.draw()
        
    def increase(self,vcurrent=1,draw=True):
        self.setAmount( self.vcurrent + vcurrent )
        if (draw): self.draw()
        
    def draw(self):
        if self.pbar != self.pbarOld:
            self.pbarOld = self.pbar
            sys.stdout.write('\r'+self.pbar)
            sys.stdout.flush()
            
    def close(self):
        sys.stdout.write('\n')
