import arepy as apy
import numpy as np

# Similar function like collector.py but this collects data of any shape

class heap:
    def __init__(self):
        self.items = {}

    def __getitem__(self,name):
        return self.items[name]

    def add(self,key,values):
        if key not in self.items:
            self.items[key] = np.array(values)
        else:
            if self.items[key].ndim>1: 
                self.items[key] = np.vstack((self.items[key],values))
            else:
                self.items[key] = np.hstack((self.items[key],values))
        
    
