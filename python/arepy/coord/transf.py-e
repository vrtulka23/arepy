import numpy as np
import arepy as apy

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
        if 'box' in opt:
            center = (opt['box'][::2]+opt['box'][1::2])*0.5
            radius = np.linalg.norm(opt['box'][1::2]-opt['box'][::2])*0.5
            self.addSelection('select','sphere', center=center, radius=radius, box=opt['box'])
        elif 'center' in opt:
            if 'radius' in opt:
                self.addSelection('select','sphere', center=opt['center'], radius=opt['radius'])
            elif 'size' in opt:
                radius = opt['size']*np.sqrt(3)*0.5
                box = apy.coord.box(opt['size'],opt['center'])
                self.addSelection('select','sphere', center=opt['center'], radius=radius, box=box)
        # translate coordinates
        if 'origin' in opt:
            self.addTranslation('translate', opt['origin'])
            if 'box' in opt:
                opt['box'] = self.convert('translate',opt['box'],dims=[0,0,1,1,2,2])
            if 'center' in opt:
                opt['center'] = self.convert('translate',opt['center'],dims=[0,1,2])
        # align z-axis to some vector
        if 'align' in opt:
            self.addAlignment('align', opt['align'])
        # flip axes
        if 'flip' in opt:
            self.addFlip('flip', opt['flip'])
        # rotate axis by an angle
        if 'rotate' in opt:
            self.addRotation('rotate', opt['rotate'])
        # post-select
        if 'box' in opt:
            self.addSelection('crop','box', box=opt['box'])
        elif 'center' in opt:
            if 'radius' in opt:
                if 'theta' in opt:
                    self.addSelection('crop','cone', center=opt['center'], radius=opt['radius'], theta=opt['theta'])
                else:
                    box = apy.coord.box(opt['radius']*2/np.sqrt(3),opt['center'])                
                    self.addSelection('crop','sphere', center=opt['center'], radius=opt['radius'], box=box)
            elif 'size' in opt:
                self.addSelection('crop','box', box=apy.coord.box(opt['size'],opt['center']))
                
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
            if 'dims' in opt:
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
        elif ttype=='sphere':     # select spherical region around center
            x,y,z = (coord-opt['center']).T
            ids = (x*x + y*y + z*z) < opt['radius']**2
            self.items[name]['ids'] = ids
            if np.ndim(coord)>1:
                coord = coord[ids]  # selector returns 2D array even though it was 1D before
            else:
                coord = None if ids is False else coord
        elif ttype=='cone':       # select conical region around the center
            x,y,z = (coord-opt['center']).T
            theta = np.arccos( z / np.sqrt(x*x + y*y + z*z) )   # inclination 
            if (opt['theta']>0):  # around z-axis
                ids = (theta < opt['theta'])  | ( (np.pi-opt['theta']) < theta ) 
            else:                 # around x/y-plane
                ids = (-opt['theta'] < theta) | (theta < (opt['theta']+np.pi) )
            self.items[name]['ids'] = ids
            if np.ndim(coord)>1:
                coord = coord[ids]  # selector returns 2D array even though it was 1D before
            else:
                coord = None if ids is False else coord
        elif ttype=='box':        # select a box region
            x,y,z = coord.T
            ids =  (opt['box'][0]<x) & (x<opt['box'][1]) &\
                   (opt['box'][2]<y) & (y<opt['box'][3]) &\
                   (opt['box'][4]<z) & (z<opt['box'][5])
            self.items[name]['ids'] = ids
            coord = coord[ids]
        elif ttype=='flip':
            coord = coord.T[opt['axes']].T
        return coord

    def addSelection(self, name, stype, **opt):       # Example: box=[0,1,0,1,0,1], center=[0.5,0.5,0.5], radius=0.5
        opt['type'] = stype
        self.items[name] = opt
        '''
        if len(opt)==3:
            self.items[name] = {'type':'sphere', 'center':opt[0], 'radius':opt[1], 'box':opt[2]}
        elif len(opt)==2:
            self.items[name] = {'type':'sphere', 'center':opt[0], 'radius':opt[1]}
        else:
            self.items[name] = {'type':'box', 'box':opt[0]}
        '''
        
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
