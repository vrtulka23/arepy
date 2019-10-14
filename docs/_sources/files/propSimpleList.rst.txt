Simple properties
*****************

.. contents:: Contents
   :local:

Property functions
^^^^^^^^^^^^^^^^^^

Simple properties are directly taken or derived from the snapshot properties.

Every property called <NAME> is defined as:

.. py:function:: prop_<NAME>(ids, ptype, **prop)
		 
    :param list[bool] ids: Particle IDs selectors
    :param int ptype: Particle type
    :param dict prop: Dictionary with additional properties
    
In the class descriptions below we will list only additional parameters included in the *prop* dictionary.

Basic properties
^^^^^^^^^^^^^^^^

.. autoclass:: arepy.files.prop.simple
   :members:

Basic selectors
^^^^^^^^^^^^^^^

.. autoclass:: arepy.files.prop.simpleSelect
   :members:

Basic mathematical functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: arepy.files.prop.simpleMath
   :members:

Basic statistical functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: arepy.files.prop.simpleStat
   :members:

SGChem properties
^^^^^^^^^^^^^^^^^

.. autoclass:: arepy.files.prop.sgchem1
   :members:


Sink particle properties
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: arepy.files.prop.sink
   :members:

Sink particle selectors
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: arepy.files.prop.sinkSelect
   :members:
