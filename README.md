# arepy

## Description
This module can be used for analysis of the Arepo files and snapshots.
It is primarily written in Python (v3.7+) and could be directly used as a Python module.
One can directly include it into the $PYTHONPATH variable through `.bashrc`:
```
export PYTHONPATH=$PYTHONPATH:$HOME/path/to/module/
```
It also uses Bash scripts so it can be directly operated from the terminal without any GUI.

## Parts

| Dir          | Description                                          |
|--------------|------------------------------------------------------|
| coord        | routines for work with the coordinates               |		
| data         | routines for work with the data                      |
| files        | scripts that hanle Arepo files and snapshots         |
| phys         | physical equations and tests                         |
| plot         | plotting routines                                    |
| scripy       | script-py, project hanling                           |
| shell        | shell scripts                                        |
| util         | various utilities                                    |
| constants.py | physical constants                                   |
| units.py     | unit handling                                        |

## Example of use

### How to get an arbitrary property from a snapshot?

There are two types of properties:
* simple properties that can be calculated directly are defined in `files/snapSimple.py`
* complex properties, that are composed using simple properties are defined in `files/snapComplex.py`

Each property can be called as a dictionary with the following form:
```
{'name':'Property','ptype':0,... special options}
```
where `ptype` stands for the Arepo particle type. 
If `ptype` is not given it is defaultly set to 0 (gas).
For convenience, simple gas properties can be also called by their string names `'Property'`.

#### Simple properties
It is straightforward to call simple properties from a snapshot. For example
```
masses = snap.getProperty('Masses')
```
is equal to
```
masses = snap.getProperty({'name':'Masses','ptype':0})
```
One can even call multiple properties at once simply by asking for an array of properties
```
masses,coordinates = snap.getProperty(['Masses',{'name':'Coordinates','ptype':5}])
```

#### Complex properties
Complex properties use combinations of simple properties and often require some additional options.
For example this query creates a projected image of the gas `NumberDensity`:
```
img = snpa.getProperty({'name':'BoxRegion','box':[xmin,xmax,ymin,ymax,zmin,zmax]})
```

## Licensing and contribution
Everybody is welcomed to use this code for private or research purpouse in terms of its license.
Contributions to the code should be consulted with the author.
