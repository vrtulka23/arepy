import numpy as np
import arepy as apy
import copy

class transf:
    """Coordinate transformations

    :param bool show: Print out transformation information
    :param region: Coordinate region
    :type region: :class:`arepy.coord.box` or :class:`arepy.coord.sphere` or :class:`arepy.coord.cone`
    :param [float]*3 origin: New coordinate origin
    :param [float]*3 align: Vector of a new z-axis
    :param [int] flip: New order of the axis
    :param [float] rotate: Euler rotation angles

    There is a standard sequence of transformations that can be used during the initialization of this class:
    
    1) **select** - Select an initial spherical region from coordinates
    2) **translate** - Set a new origin of the selected coordinates (e.g. center of the sphere)
    3) **align** - Align the z-axis with some given vector (e.g. angular momentum)
    4) **flip** - Flip axes (e.g. exchange y and z axes)
    5) **rotate** - Add some additional rotation to the region
    6) **crop** - Select a final region shape (e.g. box)

    A simple initialization will look like::
        
        import arepy as apy
        import numpy as np
        
        transf = apy.coord.transf(
            region = apy.coord.box([0.2,0.8,0.2,0.8,0.2,0.8]),
            origin = [0.5,0.5,0.5],
            align = [0.3,0.5,0.0],
            flip = [0,2,1],
            rotate = [0,0,np.pi/5],
        )

    However, it is always possible to set an arbitrary list of transformations::
        
        transf = apy.coord.transf()
        transf.addSelection('sphere', apy.coord.sphere([0.2,0.8,0.2],0.8) )
        transf.addTranslation('shift', [0.2,0.8,0.2])
    """
    
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        True

    def __init__(self,show=False,**opt):
        self.items = {}   # list of added transformations    
        
        # pre select coordinates
        if 'region' in opt:
            region = opt['region'].getCopy()
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
            self.addSelection('crop', region=region.getBox() )
                
        # print out the settings for debugging
        if show:
            for key,val in self.items.items():
                print(key)
                for k,v in val.items():
                    print('   ',k,v)    

    def __getitem__(self, name):
        if name in self.items:
            return self.items[name]
        else:
            apy.shell.exit("A transformation called '%s' is not defined. (transf.py)"%name)

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

    def convert(self, name, coord, **opt):
        """Perform selected transformations 

        :param name: Name or names of the transformations
        :type name: str or list[str]
        :param list[[float]*len(dims)] coord: List of coordinates/vectors
        :param list[int] dims: Dimensions of the vectors (default is [0,1,2])
        :return: Transformed coordinates

        Initialized transformations can be applied on the set of coordinates::
            
            coord = np.random.rand(20,3)
            coord = transf.convert(['select','flip','crop'], coord)

        It is also possible to convert vectors with an arbitrary set of dimensions.
        In the following case we are transforming the limits of a box region, where the vector dimensions
        are [x,x,y,y,z,z]::
                        
            limits = [0.2,0.8,0.2,0.8,0.2,0.8]
            limits = transf.convert(['select','flip','crop'], limits, dim=[0,0,1,1,2,2])
        """
        coord = np.array(coord)
        names = [name] if isinstance(name,str) else name
        for name in names:
            if name not in self.items: # skipping non-existing transformations
                continue
            coord = self._transf(name,coord,**opt)
        return coord

    def select(self, name, data):  
        """Select data corresponding to the coordinate region

        :param str name: Name of the region transformation
        :param data: Data with the same length as the initial array with the coordinates 
        :return: Data selected for the particles within the region

        This function is used in the case when we have an additional dataset that corresponds to the
        coordinates (e.g. masses of the particles) and we want to additionally select its corresponding values::
                    
            coord = np.random.rand(20,3)
            masses = np.random.rand(20)
            coord = transf.convert(['select','flip','crop'], coord)
            masses = transf.select('crop',masses)
        """
        if name not in self.items: # skipping non-existing transformations
            return data    
        else:
            return data[ self.items[name]['ids'] ]

    def addSelection(self, name, **opt):
        """Add selection

        :param str name: Name of the transformation
        :param region: Coordinate region
        :type region: :class:`arepy.coord.box` or :class:`arepy.coord.sphere` or :class:`arepy.coord.cone`
        """
        opt['type'] = 'selection'
        self.items[name] = opt
        
    def addTranslation(self, name, origin):
        """Add a translation
        
        :param str name: Name of the transformation
        :param [float]*3 origin: Coordinates of the new origin
        """
        self.items[name] = {'type':'translation', 'origin':origin}

    def addAlignment(self, name, vector):
        """Add an alignment

        :param str name: Name of the transformation
        :param [float]*3 vector: Vector of a new z-axis
        """
        x,y,z = vector
        theta = np.arctan2( np.sqrt(x*x+y*y), z )  
        phi = np.arctan2( y, x )
        self.items[name] = {'type':'rotation', 'angles':[0,-theta,-phi], 'order':[2,1], 'vector':vector}
        
    def addRotation(self, name, angles):
        """Add a rotation

        :param str name: Name of the transformation
        :param [float] angles: Euler rotation angles
        """
        self.items[name] = {'type':'rotation', 'angles':angles}

    def addFlip(self, name, axes):
        """Flip axes

        :param str name: Name of the transformation
        :param [int]*3 axes: New order of the axes
        """
        self.items[name] = {'type':'flip', 'axes':axes}

    def show(self):
        """Print out all transformation into the command line"""
        for key,val in self.items.items():
            print('>>>',key)
            for k,v in val.items():
                if k=='region':
                    v.show()
                else:
                    print(k, v)
