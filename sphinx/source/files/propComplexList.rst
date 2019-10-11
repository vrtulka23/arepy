Complex properties
******************

.. contents:: Contents
   :local:

Property functions
^^^^^^^^^^^^^^^^^^

Complex properties can make use of all properties and combine them to more complex functions and data reduction. 

Every property called <NAME> is defined as:

.. py:function:: prop_<NAME>(ids, ptype, **prop)
		 
    :param list[bool] ids: Particle IDs selectors
    :param int ptype: Particle type
    :param dict prop: Dictionary with additional properties
    
In the class descriptions below we will list only additional parameters included in the *prop* dictionary.

Various
^^^^^^^

.. autoclass:: arepy.files.snap.prop.complex
   :members:

Regions
^^^^^^^

.. autoclass:: arepy.files.snap.prop.complexRegion
   :members:

Slices
^^^^^^

.. autoclass:: arepy.files.snap.prop.complexSlice
   :members:

Projections
^^^^^^^^^^^

.. autoclass:: arepy.files.snap.prop.complexProj
   :members:
