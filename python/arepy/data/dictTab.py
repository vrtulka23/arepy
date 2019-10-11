import arepy as apy
import numpy as np

# dictTab will be formated as follows
#  [key],[(val),(val),(val)]          -> [{dict},{dict},{dict}]
#  [key],{'':(val),'':(val),'':(val)} -> {'':{dict},'':{dict},'':{dict}]

class dictTab:
    """Dictionary table

    :var list[dict] or dict[dict] items: List of items
    :var int size: Size of the list
    :var list[str] keys: Column names (keys)
    :param list[str] keys: Column names (keys)
    :param items: List of table rows (values)
    :key items: list[tuple] or dict[dict]
    :return: Object of self

    This purely cosmetic function converts tabulated parameters 
    into a list of dictionaries. It makes the code a bit neater and more readable

    Examples:
    
    1) Return a list::
           
           >>> props = apy.data.dictTab(['key','label','scale'],[
           >>>     ('X_H2',     '$X_\mathrm{H_2}$','lin'),
           >>>     ('Mass',     'M ($M_\odot$)',   'log'),
           >>> ])
           >>> props.items
    
           [{'key':'X_H2', 'label':'$X_\mathrm{H_2}$', 'scale':'lin'}
            {'key':'Mass', 'label':'M ($M_\odot$)', 'scale':'log'}]

    2) Return a dictionary::
           
           >>> props = apy.data.dictTab(['key','label','scale'],{
           >>>     "item1": ('X_H2',     '$X_\mathrm{H_2}$','lin'),
           >>>     "item2": ('Mass',     'M ($M_\odot$)',   'log'),
           >>> })
           >>> props.items
    
           {"item1": {'key':'X_H2', 'label':'$X_\mathrm{H_2}$', 'scale':'lin'}
            "item2": {'key':'Mass', 'label':'M ($M_\odot$)', 'scale':'log'}}

    """
    
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
        """Add rows to the table

        :param touple items: Table row (dictionary values)
        """
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

    def getKeys(self):
        return list(self.items.keys())
    def getValues(self):
        if isinstance(self.items,dict):
            return list(self.items.values())
        else:
            return self.items

    def getColumn(self,col):
        """Get column from a table

        :param str col: A dictionary key to select
        :return list: List of values selected by a key
        """
        return [item[col] for item in self.items]
    
    def correlate(self):
        """Return a correlation of the items

        :return: Data correlation list
        :rtype: :class:`arepy.data.correlate`
        """
        return apy.data.correlate(self.items)
