Example project
***************

.. contents:: Contents
   :local:

In this small tutorial we will show following:

* Setup a new project called "example"
* Create initial conditions for a H2 region expansion
* Run the simulations
* Analyze data and create several plots and tables

New project
^^^^^^^^^^^

First of all we need to setup a new project:

.. code:: bash
	  
    apy --init-project example

The above command will create a new project directory and a project class where you will store all general simulation settings:

| **./python/scripy/example** (project directory)
| **./python/scripy/example/__init__.py**. (project class)

Newly created project is now a standard Python module that can be in principle imported from any Python script.
However, we will use it only indirectly in the following scripts.
For more description of the project class refer to :class:`arepy.scripy.project`.

Before we procede to the next step please set in the **__init__.py** file your prefered simulation directory::

    self.dirSim = "/my/simulation/directory"

New simulation setup
^^^^^^^^^^^^^^^^^^^^

In this part we will create initial condition to test a Stromgren sphere.

As you may have noticed in the previous step the project class includes a first simulation.
Lets modify its default settings to something like this::
    
    self.sims['001'] = {
        'name':'example',
        'setup':'stromgren',
        'job':{'nodes':1,'proc':16,'time':'1:00:00','type':'standard'},
        'units':{'length':apy.const.pc,'time':apy.const.yr},
    }

Here you may notice that the simulation '001' with name 'example' is initialized by setup 'stromgren'.
Therefore, lets go to our simulation directory and create a new setup:

.. code:: bash

    cd /my/simulation/directory
    apy --init-setup stromgren

The above script will create several new files:

| **./python/scripy/example/setups**
| **./python/scripy/example/setups/__init__.py**
| **./python/scripy/example/setups/stromgren** (setup directory)
| **./python/scripy/example/setups/stromgren/__init__.py** (setup class)

The most important is the last file, because it contains all the setup directives for the simulation.

Simple initial conditions
^^^^^^^^^^^^^^^^^^^^^^^^^

In order to make simple initial conditions for our HII region we can modify the setup class, that we created in the previous step.
For more description of the setup class refer to :class:`arepy.scripy.setup`.

First, we will set the resolution of a desired grid::

    def init(self):
        self.opt['nRes'] = 64

Download this configuration file (Config.sh_) and copy it to the setup directory.
We will use a class :class:`arepy.files.config` to read the configuration file from the setup directory, modify and save it to the simulation directory.
All the parameters are already preset, so we will use it as it is::

    def setupConfig(self,fileName,defValues):
        with apy.files.config(self.dirSetup+'/Config.sh') as f:
            f.setValue(defValues)
            f.write(fileName)

.. _Config.sh: data/Config.sh

Do the same with the parameter file (param.txt_) and update the corresponding setup function.
In this case we will use a class :class:`arepy.files.param`::

    def setupParam(self,fileName,defValues):
        with apy.files.param(self.dirSetup+'/param.txt') as f:
            f.setValue(defValues)
            f.write(fileName)

.. _param.txt: data/param.txt

Optionally you can add also a run script that is used to store job parameters.
For this refer to the class :class:`arepy.files.runsh` and modify the setup scirpt as follows::

    def setupRun(self,fileName,defValues):
        with apy.files.runsh() as f:
            f.setValue(defValues)
            f.write(fileName)

The simulation will have only a one ideal source (with emission of 1e50 photons per second) in the center (coordinates [0.5,0.5,0.5]) of the box.
We can easily setup a corresponding file with sources using the class :class:`arepy.files.sources`::

    def setupSources(self,fileName):
        coord = [0.5,0.5,0.5]              # in code units (BoxSize=1)
        sed = [ 0.0, 0.0, 1e50, 0.0, 0.0 ] # in photons per second
        with apy.files.sources() as f:
            f.addSource(coord,sed)
            f.write(fileName)

Finally, we have to create file with initial conditions and particle grid using the class :class:`arepy.files.snap`.
The corresponding part in the setup will look like this::

    def setupIcs(self,fileIcs):
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

Remove other uncesessary functiona and save the setup file.
Now we are ready to create the simulation directory with all its files.
This step is also very easy, the simulation can be created using the following call in the command line:

.. code:: bash
   
   apy --setup 001

Here we use the simulation name '001' that was used with settings in the project class.

The above command will create following files in your simulation directory:

* **001_example**
* **001_example/Config.sh**
* **001_example/ics_32.hdf5**
* **001_example/output**
* **001_example/param.txt**
* **001_example/rad_sources.bin** 
* **001_example/run.sh**

It is also possible to update only selected parts of the setup, by adding some extra arguments to the call above::

.. code:: bash
   
    apy --setup 001 param config

