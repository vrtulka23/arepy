import numpy as np
import arepy as apy
import copy

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

    def __init__(self,show=False,**opt):
        self.items = {}   # list of added transformations    

        # pre select coordinates
        if 'region' in opt:
            region = copy.copy(opt['region']) # copy the object before applying changes
            self.addSelection('select', region=region.getSphere() )
        # translate coordinates
        if 'origin' in opt:
            self.addTranslation('translate', opt['origin'])
            if 'region' in opt:
                region.setTranslation(opt['origin'])
        # align z-axis to some vector
        if 'align' in opt:
            self.addAlignment('align', opt['align'])
        # flip axes
        if 'flip' in opt:
            self.addFlip('flip', opt['flip'])
            if 'region' in opt:
                region.setFlip(opt['flip'])
        # rotate axis by an angle
        if 'rotate' in opt:
            self.addRotation('rotate', opt['rotate'])
        # post-select
        if 'region' in opt:
            self.addSelection('crop', region=region)
                
        # print out the settings for debugging
        if show:
            for key,val in self.items.items():
                print(key)
                for k,v in val.items():
                    print('   ',k,v)    

    def __getitem__(self, name):
        return self.items[name]

    def _rotEuler(self,coord,angles):
        # Formalism: https://en.wikipedia.org/wiki/Rotation_formalisms_in_three_dimensions
        # [phi,theta,psi] are euler angles around [x,y,z] axis respectively
        # One can use spherical coordinates [r,theta,phi] as euler angles [0,theta,phi]
        cPhi,   sPhi   = np.cos(angles[0]), np.sin(angles[0])
        cTheta, sTheta = np.cos(angles[1]), np.sin(angles[1])
        cPsi,   sPsi   = np.cos(angles[2]), np.sin(angles[2])
        x,y,z = coord.T    # set of vectors v=(x,y,z) reshaping from (N,3) to (3,N)
        coord = np.array([ # calculating A*v = Az*Ay*Ax*v
            x*(cTheta*cPsi) + y*(-cPhi*sPsi+sPhi*sTheta*cPsi) + z*(sPhi*sPsi+cPhi*sTheta*cPsi),  # x*a11+y*a12+z*a13
            x*(cTheta*sPsi) + y*(cPhi*cPsi+sPhi*sTheta*sPsi) +  z*(-sPhi*cPsi+cPhi*sTheta*sPsi), # x*a21+y*a22+z*a23
            x*(-sTheta) +     y*(sPhi*cTheta) +                 z*(cPhi*cTheta),                 # x*a31+y*a32+z*a33
        ]).T              # returning to shape (N,3)
        return coord

    def _gridSelect(self, coord, grid):
        from scipy.spatial import cKDTree
        kdt = cKDTree(coord)
        dist,ids = kdt.query(grid)            
        return ids

    def _transf(self, name, coord, **data):
        ttype = self.items[name]['type']
        opt = self.items[name]
        if ttype=='translation':  # translate origin
            if 'dims' in data:
                coord -= opt['origin'][data['dims']]
            else:
                coord -= opt['origin']
        elif ttype=='rotation':   # rotate around the origin
            if 'order' in opt:
                for o in opt['order']:
                    angles = [0,0,0]
                    angles[o] = opt['angles'][o]
                    coord = self._rotEuler(coord,angles)
            else:
                coord = self._rotEuler(coord,opt['angles'])
        elif ttype=='selection':     # select coordinates from a region
            self.items[name]['ids'], coord = opt['region'].selectCoordinates(coord)
        elif ttype=='flip':
            coord = coord.T[opt['axes']].T
        return coord

    def addSelection(self, name, **opt):       # Example: box=[0,1,0,1,0,1], center=[0.5,0.5,0.5], radius=0.5
        opt['type'] = 'selection'
        self.items[name] = opt
        
    def addTranslation(self, name, origin):   # Example: coordinates=[x,y,z]
        self.items[name] = {'type':'translation', 'origin':origin}

    def addAlignment(self, name, vector):     # Example: vector=[x,y,z]
        x,y,z = vector
        theta = np.arctan2( np.sqrt(x*x+y*y), z )  
        phi = np.arctan2( y, x )
        self.items[name] = {'type':'rotation', 'angles':[0,-theta,-phi], 'order':[2,1], 'vector':vector}
        
    def addRotation(self, name, angles):      # Example: angles=[phi,theta,psi] in radians
        self.items[name] = {'type':'rotation', 'angles':angles}

    def addFlip(self, name, axes):            # Example: axes=[1,0,2] 
        self.items[name] = {'type':'flip', 'axes':axes}

    def select(self, name, data):  # select additional data
        if name not in self.items: # skipping non-existing transformations
            return data    
        else:
            return data[ self.items[name]['ids'] ]

    def convert(self, name, coord, **opt):  # convert vector
        coord = np.array(coord)
        names = [name] if isinstance(name,str) else name
        for name in names:
            if name not in self.items: # skipping non-existing transformations
                continue
            coord = self._transf(name,coord,**opt)
        return coord

    # print out all transformations
    def show(self):
        for key,val in self.items.items():
            print('>>>',key)
            for k,v in val.items():
                if k=='region':
                    v.show()
                else:
                    print(k, v)
