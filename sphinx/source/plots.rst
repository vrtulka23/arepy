Plotting and analysis
*********************

.. contents:: Contents
   :local:

Defining a new plot
^^^^^^^^^^^^^^^^^^^

It is possible to initialize and create PLOTs directly from your command line.
For this you have to be in a PROJECT directory.

The following command

.. code-block:: bash    

   apy --init-plot PLOT

will create:

1) A new plot directory: **./python/scripy/PROJECT/plots/PLOT**

2) Default plot class: **./python/scripy/PROJECT/plots/PLOT/__init__.py**

   The class implements three basic methods::
        
       import arepy as apy
       import numpy as np
       
       class PLOT(apy.scripy.plot):
       
            def settings(self):
                # Some general settings go here...
         
            def init(self):
                # Plot initialization goes here...
         
            def plot(self):
                # Plotting routine goes here...

Additionally, it is possible to split the PLOT class into several SUBPLOT classes and store them in separate files.

a) One parent class that contains general plot settings

   **./python/scripy/PROJECT/plots/PLOT/__init__.py**

   ::

       import arepy as apy
       import numpy as np

       class PLOT(apy.scripy.plot):
           
           def settings(self):
               # Some general settings go here...
        
b) One or several subplot classes that inherit the parent class

   **./python/scripy/PROJECT/plots/PLOT/SUBPLOT.py**

   ::

       import arepy as apy 
       import numpy as np
       from scripy.PROJECT.plots.PLOT import PLOT
     
       class SUBPLOT(PLOT):
   
           def init(self):
               # Plot initialization goes here...
      
           def plot(self):
               # Plotting routine goes here...


Plot class
^^^^^^^^^^

.. autoclass:: arepy.scripy.plot
   :members:

Plotting the data
^^^^^^^^^^^^^^^^^

Plots can be subsequently called from the command line in three ways:

1) Using the following command

   .. code-block:: bash
		
       apy --plot PLOT [SUBPLOT]

   figures will be saved as
  
   **./results/PROJECT/PLOT/PLOT/000000_0000/PLOT000.png**
   
   or 

   **./results/PROJECT/PLOT/SUBPLOT/000000_0000/SUBPLOT000.png**

   where 000000_0000 is a current time-stamp and 000 is a figure number.
   
2) In order to avoid many subfolders while debugging one can use also the following command:

   .. code-block:: bash
       
       apy --debug PLOT [SUBPLOT]

   In this case the figure are stored as

   **./results/PROJECT/PLOT/SUBPLOT/debug/SUBPLOT000.png**


3) Finally, it is also possible to display the last created plot without recalculating the values:
   
   .. code-block:: bash
       
       apy --show PLOT [SUBPLOT]
