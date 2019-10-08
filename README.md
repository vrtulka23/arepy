# `arepy`

## Description

`arepy` is a python module that can be used to analyse Arepo output files and snapshots.

It is primarily written in Python (v3.7+), but some parts are written in BASH.

This module requires `numpy`, `scipy` and `h5py` python modules.

`scripy` is a collection of user created scripts to setup, manage and analyze Arepo simulations

## File structure

| File/directory | Description |
|---|---|
| private | a directory for your privat data and files that will not synchronize with the `arepy` |
| python | directory included in $PYTHONPATH with the `arepy` and `scripy` scripts |
| &nbsp; &nbsp;![/arepy](https://github.com/vrtulka23/arepy/tree/master/python/arepy) | arepy python scripts (main arepy module) |
| &nbsp; &nbsp; &nbsp; &nbsp;![/coord](https://github.com/vrtulka23/arepy/tree/master/python/arepy/coord) | routines for coordinate manipulation |
| &nbsp; &nbsp; &nbsp; &nbsp;![/data](https://github.com/vrtulka23/arepy/tree/master/python/arepy/data) | routines for dataset manipulation |
| &nbsp; &nbsp; &nbsp; &nbsp;![/files](https://github.com/vrtulka23/arepy/tree/master/python/arepy/files) | routines that open/edit/wirte Arepo files and simulations |
| &nbsp; &nbsp; &nbsp; &nbsp;![/phys](https://github.com/vrtulka23/arepy/tree/master/python/arepy/phys) | routines with various physical/analytical models and functions |
| &nbsp; &nbsp; &nbsp; &nbsp;![/plot](https://github.com/vrtulka23/arepy/tree/master/python/arepy/plot) | standardized plotting routines |
| &nbsp; &nbsp; &nbsp; &nbsp;![/scripy](https://github.com/vrtulka23/arepy/tree/master/python/arepy/scripy) | `scripy` classes and templates |
| &nbsp; &nbsp; &nbsp; &nbsp;![/shell](https://github.com/vrtulka23/arepy/tree/master/python/arepy/shell) | python routines that work with a bash shell |
| &nbsp; &nbsp; &nbsp; &nbsp;![/util](https://github.com/vrtulka23/arepy/tree/master/python/arepy/util) | various python routines and utilities |
| &nbsp; &nbsp;![/scripy/PROJECT](https://github.com/vrtulka23/arepy/tree/master/python/scripy) | project directory |
| &nbsp; &nbsp; &nbsp; &nbsp;/plots/PLOT | plotting scripts |
| &nbsp; &nbsp; &nbsp; &nbsp;/setups/SETUP | simulation setup scripts  |
| results | directory which stores figures and tables created by `scripy` scripts |
| ![shell](https://github.com/vrtulka23/arepy/tree/master/shell) | shell scripts and system settings |
| &nbsp; &nbsp;![/systems/SYSTEM.sh](https://github.com/vrtulka23/arepy/tree/master/shell/systems) | predefined system settings |

## Installation

Installation of the `arepy` is very simple!

Go to the main `arepy` directory that you cloned from this website and run the installation BASH script:
```
cd $HOME/path/to/arepy
sh install.sh
```
The installation script will ask you to include `python/` directory into your local $PYTHONPATH and also to create an alias for the `arepy` bash script `shell/run.sh`.

After this the `arepy` python module can be included in any python script and you will be also able to use `arepy` shell scripts from your terminal.

In the next step you will have to choose system settings. You can either choose existing settings by inputing one of the system names in `shell/systems/{SYSTEM_NAME}.sh` or create a new one by putting your own name.

Arepo source code can be either stored directly in the arepy main directory `/path/to/arepy/arepo/(source code)`, or you can set your own path to the `shell/system.sh` as:

```bash
DIR_AREPO=/my/path/to/arepo
```

## Documentation and examples

For more information see the ![documentation](https://vrtulka23.github.io/arepy/index.html).

## Licensing and contribution
Everybody is welcomed to use this code for private or research purpouse in terms of its license.
Contributions to the code should be consulted with the author.
