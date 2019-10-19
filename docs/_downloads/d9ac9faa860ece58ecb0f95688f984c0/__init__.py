import arepy as apy
import numpy as np

class setup(apy.scripy.setup):
    """Setup class of a project 'example'
    
    This setup class inherits :class:`arepy.scripy.setup` class.
    """

    def init(self):
        """Initial settings

        Here we set the resolution of a desired grid:

        .. literalinclude:: ../../python/scripy/examples/setups/emptybox/__init__.py
            :language: python
            :lines: 19
        """
        self.opt['nRes'] = 64

    def setupConfig(self,fileName,defValues):
        """Setup a configuration file

        Download this configuration file (:download:`Config.sh <../../python/scripy/examples/setups/emptybox/Config.sh>`) 
        and copy it to the setup directory. 
        We will use a class :class:`arepy.files.config` to read the configuration file from the setup directory, 
        modify and save it to the simulation directory. 
        All the parameters are already preset, so we will use it as it is:        

        .. literalinclude:: ../../python/scripy/examples/setups/emptybox/__init__.py
            :language: python
            :lines: 34-36
        """
        with apy.files.config(self.dirSetup+'/Config.sh') as f:
            f.setValue(defValues)
            f.write(fileName)

    def setupParam(self,fileName,defValues):
        """Setup a parameter file

        Do the same with the parameter file (:download:`param.txt <../../python/scripy/examples/setups/emptybox/param.txt>`) 
        and update the corresponding setup function. 
        In this case we will use a class :class:`arepy.files.param`:

        .. literalinclude:: ../../python/scripy/examples/setups/emptybox/__init__.py
            :language: python
            :lines: 49-51
        """
        with apy.files.param(self.dirSetup+'/param.txt') as f:
            f.setValue(defValues)
            f.write(fileName)

    def setupRun(self,fileName,defValues):
        """Setup a job script file

        Optionally you can add also a run script that is used to store job parameters. 
        For this refer to the class :class:`arepy.files.runsh` and modify the setup scirpt as follows:

        .. literalinclude:: ../../python/scripy/examples/setups/emptybox/__init__.py
            :language: python
            :lines: 63-65
        """
        with apy.files.runsh() as f:
            f.setValue(defValues)
            f.write(fileName)

    def setupSources(self,fileName):
        """Setup a file with sources

        The simulation will have only a one ideal source (with emission of 1e50 photons per second) 
        in the center (coordinates [0.5,0.5,0.5]) of the box. 
        We can easily setup a corresponding file with sources using the class :class:`arepy.files.sources`:

        .. literalinclude:: ../../python/scripy/examples/setups/emptybox/__init__.py
            :language: python
            :lines: 78-82
        """
        coord = [0.5,0.5,0.5]              # in code units (BoxSize=1)
        sed = [ 0.0, 0.0, 1e50, 0.0, 0.0 ] # in photons per second
        with apy.files.sources() as f:
            f.addSource(coord,sed)
            f.write(fileName)

    def setupIcs(self,fileName):
        """Setup initial conditions

        Finally, we have to create file with initial conditions and particle grid using the class :class:`arepy.files.snap`. 
        The corresponding part in the setup will look like this:

        .. literalinclude:: ../../python/scripy/examples/setups/emptybox/__init__.py
            :language: python
            :lines: 94-132
        """
        with apy.files.snap(fileIcs,fmode='w') as f:

            # set a file header
            ngas = self.opt['nRes']**3
            f.setHeader({
                'NumPart_ThisFile':         [ngas,0,0,0,0,0],
                'NumPart_Total':            [ngas,0,0,0,0,0],
                'NumPart_Total_HighWord':   [0]*6,
                'MassTable':                [0.0]*6,
                'Redshift':                 0.0,
                'BoxSize':                  1.0,
                'NumFilesPerSnapshot':      1,
                'Omega0':                   0.0,
                'OmegaLambda':              0.0,
                'OmegaBaryon':              0.0,
                'HubbleParam':              1.0,
                'Flag_Sfr':                 0,
                'Flag_Cooling':             0,
                'Flag_StellarAge':          0,
                'Flag_Metals':              0,
                'Flag_Feedback':            0,
                'Flag_DoublePrecision':     1,
                'Composition_vector_length':0,
                'UnitLength_in_cm':         self.units['length'],
                'UnitMass_in_g':            self.units['mass'],
                'UnitVelocity_in_cm_per_s': self.units['velocity'],
                'Time':0,
            })

            # set cell properties
            grid = apy.coord.gridCube(
                [ self.opt['nRes'] ]*3,       # number of bins in each direction
                points='centers',             # get centers of the grid cubes
                scatter=0.2/self.opt['nRes'], # add an artificial scatter
            )
            f.setProperty(0, 'Coordinates', np.array(grid.coords,dtype=np.float64) )
            f.setProperty(0, 'Masses',      np.full(ngas,1,dtype=np.float64) )
            f.setProperty(0, 'Velocities',  np.zeros((ngas,3),dtype=np.float64) )
            f.setProperty(0, 'ParticleIDs', np.arange(1,1+ngas,dtype=np.uint32) )
