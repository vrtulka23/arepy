Simple properties
*****************

Simple properties are directly taken or derived from the snapshot properties.

Every property called <NAME> is defined as:

.. py:function:: prop_<NAME>(ids, ptype, **prop)
		 
    :param list[bool] ids: Particle IDs selectors
    :param int ptype: Particle type
    :param dict prop: Dictionary with additional properties
    
In the class descriptions below we will list only additional parameters included in the *prop* dictionary.

Basic properties
^^^^^^^^^^^^^^^^

.. autoclass:: arepy.files.snap.propSimple
   :members:

Basic selectors
^^^^^^^^^^^^^^^

.. autoclass:: arepy.files.snap.propSimpleSelect
   :members:

Basic mathematical functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: arepy.files.snap.propSimpleMath
   :members:

Basic statistical functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: arepy.files.snap.propSimpleStat
   :members:

SGChem properties
^^^^^^^^^^^^^^^^^

.. autoclass:: arepy.files.snap.propSgchem1
   :members:


Sink particle properties
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: arepy.files.snap.propSink
   :members:

Sink particle selectors
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: arepy.files.snap.propSinkSelect
   :members:
