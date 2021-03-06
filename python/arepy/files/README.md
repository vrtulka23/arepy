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

# simulation files
snap = sim.getSnapshot(123)   # reads snapshot no. 123
sink = sim.getSink(123)       # reads sink snapshot no. 123
param = sim.getParameters()   # reads simulation parameter file
config = sim.getConfig()      # reads simulation configuration file

# simulation units
sim.units['time']             # conversion from code units to cgs
sim.units.conv['time']        # conversion from code units to new units
...
```

### snap.py
```python
snap = apy.files.snap('./path/to/snapshot001.hdf5')

# select only one property/header
time = snap.getHeader('Time')
masses = snap.getProperty('Masses')
print(time,masses)

# select multiple properties
header = snap.getHeader(['Time','NumPart_Total'])
props = snap.getProperty([
  'Masses',                                        # short version for gas
  {'name':'Coordinates','ptype':0},                # long version for any ptype
  {'name':'Masses','ptype':5,'key':'sinkMasses'},  # set an alternative key
])
print(header['Time'],header['NumPart_Total'][5])
print(props['Masses'], props['Coordinates'], props['sinkMasses'])
```
### sources.py
```python
src = apy.files.sources('./path/to/sources.dat')
coord = [0.5,0.5,0.5]                     # coordinates (code units)
sed = [0,0,1e49,0,0]                      # spectral emission (photons per second)
src.addSource(coord,sed)                  # add coordinates and SED of the sources
src.addCrossSections([1e-21,2e-19,...])   # add gas cross-sections (cm^2)
src.addEnergies([1e18,2e19,...])          # add photon energies (erg)
src.show()                                # show a tabulated overview of all sources

```
