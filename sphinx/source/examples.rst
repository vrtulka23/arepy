Example project
***************

.. contents:: Contents
   :local:

In this small tutorial we will show following:

* Setup a new project called "examples"
* Create initial conditions for a H2 region expansion
* Run the simulations
* Analyze data and create several plots and tables

New project
^^^^^^^^^^^

First of all we need to setup a new project:

.. code:: bash
	  
    apy --init-project examples

The above command will create a new project directory and a project class where you will store all general simulation settings:

| **./python/scripy/examples** (project directory)
| **./python/scripy/examples/__init__.py**. (project class)

Newly created project is now a standard Python module that can be in principle imported from any Python script.
However, we will use it only indirectly in the following scripts.

.. autoclass:: scripy.examples.project
   :members:

Download the :download:`source code <../../python/scripy/examples/__init__.py>` of the project class.

Simple initial conditions
^^^^^^^^^^^^^^^^^^^^^^^^^

You may have noticed that the simulation '001' with name 'hiiregion' is initialized by setup 'emptybox'.
Therefore, lets go to our simulation directory and create a new setup:

.. code:: bash

    cd /my/simulation/directory
    apy --init-setup emptybox

The above script will create several new files:

| **./python/scripy/examples/setups**
| **./python/scripy/examples/setups/__init__.py**
| **./python/scripy/examples/setups/emptybox** (setup directory)
| **./python/scripy/examples/setups/emptybox/__init__.py** (setup class)

The most important is the last file, because it contains all the setup directives for the simulation.

In order to make simple initial conditions for our HII region we can modify the setup class as follows:

.. autoclass:: scripy.examples.setups.emptybox.setup
   :members:

Download the :download:`source code <../../python/scripy/examples/setups/emptybox/__init__.py>` of the setup class.

Create simulation files
^^^^^^^^^^^^^^^^^^^^^^^

Now we are ready to create the simulation directory with all its files.
This step is also very easy, the simulation can be created using the following call in the command line:

.. code:: bash
   
   apy --setup 001

Here we use the simulation name '001' that was used with settings in the project class.

The above command will create following files in your simulation directory:

* **001_hiiregion**
* **001_hiiregion/Config.sh**
* **001_hiiregion/ics_32.hdf5**
* **001_hiiregion/output**
* **001_hiiregion/param.txt**
* **001_hiiregion/rad_sources.bin** 
* **001_hiiregion/run.sh**

It is also possible to update only selected parts of the setup, by adding some extra arguments to the call above::

.. code:: bash
    
    apy --setup 001 param config

