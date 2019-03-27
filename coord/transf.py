import numpy as np

# This works in both ways:
# 1)  tr = transf(data)
#     tr.add('translate',[0.5,0.5,0.5])
#     print tr.data
#
# 2)  tr = transf()
#     tr.add('translate',[0.5,0.5,0.5])
#     print tr.convert(data1)
#     print tr.convert(data2)

# Coordinate transformations
class transf:
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        True
    
    def __init__(self, size=None):
        self.items = {}   # list of added transformations    

    def __getitem__(self, name):
        return self.items[name]

    def _transf(self, name, data, dims):
        ttype = self.items[name]['type']
        opt = self.items[name]
        if ttype=='translation':
            data -= opt['origin'] if dims is None else opt['origin'][dims]
        elif ttype=='rotation':
            theta,phi,psi = opt['angles']
            a11,a12,a13 = np.cos(theta) , np.sin(phi)*np.sin(theta)  , np.cos(phi)*np.sin(theta)
            a21,a22,a23 = 0             , np.cos(phi)                , -np.sin(phi)
            a31,a32,a33 = -np.sin(theta), np.sin(phi)*np.cos(theta)  , np.cos(phi)*np.cos(theta)
            x,y,z = data.T
            data = np.array([ 
                x*a11 + y*a12 + z*a13, 
                x*a21 + y*a22 + z*a23, 
                x*a31 + y*a32 + z*a33
            ]).T
        elif ttype=='sphere':
            x,y,z = (data-opt['center']).T
            r2 = x*x + y*y + z*z
            ids = r2 < opt['radius']**2
            data = data[ids]
        elif ttype=='box':
            x,y,z = data.T
            ids = (opt['box'][0]<x) & (x<opt['box'][1])
            ids &= (opt['box'][2]<y) & (y<opt['box'][3])
            ids &= (opt['box'][4]<z) & (z<opt['box'][5])
        return data

    def addSelection(self, name, *opt):
        if len(opt)==3:
            self.items[name] = {'type':'sphere', 'center':opt[0], 'radius':opt[1], 'box':opt[2]}
        elif len(opt)==2:
            self.items[name] = {'type':'sphere', 'center':opt[0], 'radius':opt[1]}
        else:
            self.items[name] = {'type':'box', 'box':opt[0]}
        
    def addTranslation(self, name, origin):
        self.items[name] = {'type':'translation', 'origin':origin}
        
    def addRotation(self, name, angles):
        self.items[name] = {'type':'rotation', 'angles':angles}

    def convert(self, name, data, dims=None):  # convert vector
        data = np.array(data)
        if isinstance(name,str): # make a single transformation
            data = self._transf(name,data,dims)
        else:                    # make multiple transformations
            for n in name:
                data = self._transf(n,data,dims)
        return data
