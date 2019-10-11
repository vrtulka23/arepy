import arepy as apy
import numpy as np

class properties:
    """List of snapshot properties
    
    :param props: Single property or list of properties
    :param int ptype: Default particle type
    :key props: prop or list[prop]
    """

    def __init__(self,props=None,ptype=0):
        self.items = []         # list of items
        self.size = 0           # number of items
        self.ptype = ptype      # particle type

        self.data = {}          # dictionary for data collecting
        self.current = 0        # iterator pointer

        if props is not None:
            if isinstance(props,properties):  # simpy copy the item list
                self.items = props.items
                self.size = props.size
                self.ptype = ptype
            else:                                 # set new properties
                self.add(props)

    def add(self,props):
        """Add a new property to the list
        
        :param props: Single property or list of properties
        :key props: prop or list[prop]
        """
        items = [props] if isinstance(props,(str,dict)) else props
        for i,item in enumerate(items):
            if isinstance(item,str):          # convert to dictionary if string
                item = {'name':item}
            if 'key' not in item:             # add key if missing
                item['key'] = item['name']
            if 'ptype' not in item:           # add default particle type if missing
                item['ptype'] = self.ptype

            # decide whether the property is simple or complex
            item['complex'] = False
            if hasattr(apy.files.prop.complex,'prop_'+item['name']):
                item['complex'] = True 

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
        """Get properties as a list or dictionary
        
        :param bool dictionary: Return single property in a dictionary
        :return: Property list or a dictionary
        :rkey: list or dict
        """
        if len(self.data.values())>1 or dictionary:
            return self.data
        else:
            return list(self.data.values())[0]        

    def getWithout(self,key,values):
        """Get properties with some specific key/values
        
        :param str key: Property setting
        :param key: Values to keep
        :keys key: list[str] or str
        :return: New object of self without some properties
        """
        if not isinstance(values,list):
            values = [values]
        props = [item for i,item in enumerate(self.items) if item[key] not in values]
        return properties(props)

    def getComplex(self,add=None):
        """Select complex properties
        
        :param prop add: New properties to add
        :return: New object only with complex properties
        """
        props = properties([item for item in self.items if item['complex']])
        if add: props.add(add)
        return props

    def getSimple(self,add=None):
        """Select simple properties

        :param prop add: New Properties to add
        :return: New object only with simple properties
        """
        props = properties([item for item in self.items if not item['complex']])
        if add: props.add(add)
        return props
