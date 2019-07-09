# File classes:

## Overview

|file|class/function|description|
|---|---|---|
|config.py| config | reading and editing of an Arepo Config.sh file |
|cut.py | cut | routine for cutting regions from a simulation snapshot |
|groups.py | collection, group, item | routine for parallel analyzing caching of many snapshots |
|ics.py | ics | routine for creating initial conditions |
|image.py | image | reading of an Arepo image files |
|olist.py | olist | reading and editing of an Arepo time output list |
|param.py | param | reading and editing of an Arepo parameter file |
|runsh.py | runsh | reading and editing of a Scripy run.sh file |
|simulation.py | simulation | unifies Arepo simulation files (config, param, image,...) into one abstract class |
|sink.py | sink | reading and editing of an Arepo sink file |
|snap.py | snap | reading and editing of an Arepo snapshot file |
|snapProperties.py | snapProperties | class that acts as a list of snapshot properties |
|snapSimple.py | snapSimple | class that returns simple properties of an Arepo snapshot | 
|snapComplex.py | snapComplex | class that returns complex properties (composed from simple properties) of an Arepo snapshot |
|sources | sources | reading and editing of a SPRAI source file |
|subfind | subfind | reading of SUBFIND/FOF files |

## Examples

### simulation.py

```python
sim = apy.files.simulation('./path/to/the/simulation/directory/')
snap = sim.getSnapshot(123)   # reads snapshot no. 123
sink = sim.getSink(123)       # reads sink snapshot no. 123
param = sim.getParameters()   # reads simulation parameter file
config = sim.getConfig()      # reads simulation configuration file
sim.units['time']             # conversion from code units to cgs
sim.units.conv['time']        # conversion from code units to new units
...
```

### snap.py
```python
snap = apy.files.snap('./path/to/snapshot001.hdf5')
time = snap.getHeader('Time')
gasProps = snap.getProperty(['Masses','Coordinates'])
sinkProps = snap.getProperty([
  {'name':'Masses','ptype':5},
  {'name':'Coordinates','ptype':5},
])
print(time, gasProps['Masses'], sinkProps['Masses'])
```
