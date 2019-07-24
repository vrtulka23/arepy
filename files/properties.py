import arepy as apy
import numpy as np

# Initialize a property list with a correct format
class properties:
    def __init__(self,props=None):
        self.items = []         # list of items
        self.data = {}          # dictionary for data collecting
        self.size = 0           # number of items
        self.current = 0        # iterator pointer

        self.propsComplex = [
            'RadHistogram','BoxHistogram',
            'BoxPoints','BoxSquareXY','BoxFieldXY','BoxHealpix',
            'BoxLine','BoxLineRZ','BoxLineXYZ',
            'BoxProjCube','BoxProjCylinder',
            'AngularMomentum','MassCenter',
            'RegionCone','RegionSphere','RegionBox','RegionIds',
            'VolumeFraction'
        ]

        if props is not None:
            if isinstance(props,properties):  # simpy copy the item list
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

            # decide whether the property is simple or complex
            item['complex'] = True if item['name'] in self.propsComplex else False

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

    # set/get data
    def setData(self, key, data):
        self.data[key] = data
    def getData(self, dictionary=False):
        if len(self.data.values())>1 or dictionary:
            return self.data
        else:
            return list(self.data.values())[0]        

    # return a new object of self without some properties
    def getWithout(self,key,values):
        if not isinstance(values,list):
            values = [values]
        props = [item for i,item in enumerate(self.items) if item[key] not in values]
        return properties(props)

    # return a new object only with complex properties
    def getComplex(self,add=None):
        props = properties([item for item in self.items if item['complex']])
        if add: props.add(add)
        return props

    # return a new object only with simple properties
    def getSimple(self,add=None):
        props = properties([item for item in self.items if not item['complex']])
        if add: props.add(add)
        return props

    # return a new object of self with some new properties
