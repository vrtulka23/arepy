Example project
***************

.. contents:: Contents
   :local:

In this small tutorial we will show following:

* Setup a new project called "example"
* Create initial conditions for a H2 region expansion test using Arepo's MESHRELAX
* Run the simulations
* Analyze data and create several plots and tables

New project
^^^^^^^^^^^

First of all we need to setup a new project:

.. code:: bash
	  
    apy --init-project example

The above command will create a new project directory and a project class where you will store all general simulation settings:

| **./python/scripy/example**
| **./python/scripy/example/__init__.py**.

Newly created project is now a standard Python module that can be in principle imported from any Python script.
However, we will use it only indirectly in the following scripts.
For more description of the project class refer to :class:`arepy.scripy.project`.

Before we procede to the next step please set in the **__init__.py** file your prefered simulation directory::

    self.dirSim = "/my/simulation/directory"

New simulation setup
^^^^^^^^^^^^^^^^^^^^

In this part we will create initial condition to test a Stromgren sphere.

As you may have noticed in the previous step we also preset a first simulation.
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
| **./python/scripy/example/setups/stromgren**
| **./python/scripy/example/setups/stromgren/__init__.py**

The most important is the last file, because it contains all the setup directives for the simulation.
For more description of the setup class refer to :class:`arepy.scripy.setup`.
