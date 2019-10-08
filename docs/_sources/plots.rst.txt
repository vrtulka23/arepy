Plotting and analysis
*********************

A new plot called "PLOT" for a particular project can be initialized using the following command in the therminal:

.. code-block:: bash    
		
   apy --init-plot PLOT

Following class is a parent class for an arbitrary PLOT class, that should implement its three basic methods::
        
    import arepy as apy
    import numpy as np
     
    class PLOT(apy.scripy.plot):
     
        def settings(self):
            # Some general settings go here...
     
        def init(self):
            # Plot initialization goes here...
     
        def plot(self):
            # Plotting routine goes here...

Alternatively, it is possible to split it into several SUBPLOT classes and store them in separate files::

    class PLOT(apy.scripy.plot):
    
        def settings(self):
            # Some general settings go here...
     
    class SUBPLOT1(PLOT):

        def init(self):
            # Plot initialization goes here...
     
        def plot(self):
            # Plotting routine goes here...

    class SUBPLOT2(PLOT):

        def init(self):
            # Plot initialization goes here...
     
        def plot(self):
            # Plotting routine goes here...

Such plots can be afterwards called from the command line:

.. code-block:: bash    
		
   # Simple plot
   apy --plot PLOT [SUBPLOT]

   # Debugging plot
   apy --debug PLOT [SUBPLOT]

   # Show figure/table only
   apy --show PLOT [SUBPLOT]

Plotting class
^^^^^^^^^^^^^^

.. autoclass:: arepy.scripy.plot
   :members:
