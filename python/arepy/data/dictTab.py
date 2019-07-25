import arepy as apy
import numpy as np

# dictTab will be formated as follows
#  [key],[(val),(val),(val)]          -> [{dict},{dict},{dict}]
#  [key],{'':(val),'':(val),'':(val)} -> {'':{dict},'':{dict},'':{dict}]

class dictTab:
    def __init__(self,keys,items=None):
        self.items = None
        self.size = 0
        self.keys = keys
        if items is not None:
            self.addItems(items)

    # length operator
    def __len__(self):
        return self.size

    # object selector
    def __getitem__(self,item):
        return self.items[item]

    # object iterator
    def __iter__(self):
        self.current = 0
        return self
    def __next__(self):
        if self.current < self.size:
            self.current += 1
            return self.items[self.current-1]
        else:
            raise StopIteration

    # add new items
    def addItems(self, items):
        if isinstance(items,dict):
            if self.items is None: self.items = {}
            for name,item in items.items():
                self.items[name] = {key:item[k] for k,key in enumerate(self.keys)}
                self.size += 1
        else:
            if self.items is None: self.items = []
            items = [items] if isinstance(items,tuple) else items
            for item in items:
                self.items.append({key:item[k] for k,key in enumerate(self.keys)})
                self.size += 1            

    # return keys and values of the items
    def getKeys(self):
        return list(self.items.keys())
    def getValues(self):
        if isinstance(self.items,dict):
            return list(self.items.values())
        else:
            return self.items

    # return value of a column
    def getColumn(self,col):
        return [item[col] for item in self.items]
    
    # return a correlation array
    def correlate(self):
        return apy.data.correlate(self.items)
