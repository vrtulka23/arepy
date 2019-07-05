import arepy as apy
import numpy as np

# Initialize a property list with a correct format
class snapProperties:
    def __init__(self,props=None):
        self.items = []         # list of items
        self.size = 0           # number of items
        self.current = 0        # iterator pointer

        if props is not None:
            if isinstance(props,snapProperties):  # simpy copy the item list
                self.items = props.items
                self.size = props.size
            else:                                 # set new properties
                self.add(props)

    # add new properties into the list
    def add(self,props):
        items = [props] if isinstance(props,(str,dict)) else props
        for i,item in enumerate(items):
            if isinstance(item,str):          # convert to dictionary if string
                item = {'name':item}
            if 'key' not in item:             # add key if missing
                item['key'] = item['name']
            if 'ptype' not in item:           # add particle type if missing
                item['ptype'] = 0
            self.items.append(item)
            self.size += 1

    # select group
    def __getitem__(self,index):
        return self.items[index]

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

    # number of items
    def __len__(self):
        return self.size


    # return data in a correct shape
    def results(self,data):
        if self.size>1:
            return {item['key']:data[i] for i,item in enumerate(self.items)}
        else:
            return data[0]

    # return a new object of self without some properties
    def without(self,key,values):
        if not isinstance(values,list):
            values = [values]
        props = [item for i,item in enumerate(self.items) if item[key] not in values]
        return snapProperties(props)

    # return a new object of self with some new properties
