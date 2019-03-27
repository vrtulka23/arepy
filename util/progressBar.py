# adapted from http://code.activestate.com/recipes/578228-progress-bar-class/
#
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
    def __init__(self, vmax=100, label="", vmin = 0, nparts=50, draw=True):
        if vmax==0:
            apy.shell.exit('vmax=%d  (progressBar.py)'%(vmax))
        elif vmax<=vmin:
            apy.shell.exit('vmax=%d <= vmin=%d  (progressBar.py)'%(vmax,vmin))
        self.pbar = ""
        self.pbarOld = ""
        self.label = label if label=="" else label+" "
        self.vmin = vmin
        self.vmax = vmax
        self.span = vmax - vmin
        self.nparts = nparts - 2
        self.spanPart = self.span / float(self.nparts)
        self.amount = 0 
        self.setAmount(0)
        if draw: self.draw()

    def __str__(self):
        return str(self.pbar)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        
    def setAmount(self, amount = 0):
        if amount < self.vmin: amount = self.vmin
        if amount > self.vmax: amount = self.vmax
        self.amount = amount
        diffFromMin = float(self.amount - self.vmin)
        fractionDone = (diffFromMin / float(self.span)) * 100.0
        percentDone = int(round(fractionDone))
        numHashes = (percentDone / 100.0) * self.nparts
        hashDone = (numHashes-int(numHashes))*10.0
        numHashes = int(numHashes)
        if numHashes == 0:
            self.pbar = "[%d%s]" % (hashDone,' '*(self.nparts-1))
        elif numHashes == self.nparts:
            self.pbar = "[%s]" % ('='*self.nparts)
        else:
            self.pbar = "[%s%d%s]" % ('='*(numHashes-1),hashDone,' '*(self.nparts-numHashes))
        percentPlace = (len(self.pbar) / 2) - len(str(percentDone))
        percentString = str(percentDone) + "%"
        self.pbar = apy.shell.textc(' '.join([self.pbar, "%4s"%percentString, self.label]),'yellow')
        
    def setPercentage(self,newPercentage,draw=True):
        self.setAmount((newPercentage * float(self.vmax)) / 100.0)
        if (draw): self.draw()
        
    def increase(self,amount=1,draw=True):
        self.setAmount( self.amount + amount )
        if (draw): self.draw()
        
    def draw(self):
        if self.pbar != self.pbarOld:
            self.pbarOld = self.pbar
            sys.stdout.write('\r'+self.pbar)
            sys.stdout.flush()
            
    def close(self):
        sys.stdout.write('\n')
