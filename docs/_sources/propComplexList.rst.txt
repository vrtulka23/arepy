Complex properties
******************

Complex properties can make use of all properties and combine them to more complex functions and data reduction. 

Every property called <NAME> is defined as:

.. py:function:: prop_<NAME>(ids, ptype, **prop)
		 
    :param list[bool] ids: Particle IDs selectors
    :param int ptype: Particle type
    :param dict prop: Dictionary with additional properties
    
wIn the class descriptions below we will list only additional parameters included in the *prop* dictionary.

Various
^^^^^^^

.. autoclass:: arepy.files.snap.propComplex
   :members:

Regions
^^^^^^^

.. autoclass:: arepy.files.snap.propComplexRegion
   :members:

Slices
^^^^^^

.. autoclass:: arepy.files.snap.propComplexSlice
   :members:

Projections
^^^^^^^^^^^

.. autoclass:: arepy.files.snap.propComplexProj
   :members:
