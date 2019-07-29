# arepy

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
| &nbsp; &nbsp;/arepy | arepy python scripts (main arepy module) |
| &nbsp; &nbsp; &nbsp; &nbsp;/coord | routines for coordinate manipulation |
| &nbsp; &nbsp; &nbsp; &nbsp;/data | routines for dataset manipulation |
| &nbsp; &nbsp; &nbsp; &nbsp;/phys | routines with various physical/analytical models and functions |
| &nbsp; &nbsp; &nbsp; &nbsp;/plot | standardized plotting routines |
| &nbsp; &nbsp; &nbsp; &nbsp;/scripy | `scripy` classes and templates |
| &nbsp; &nbsp; &nbsp; &nbsp;/shell | python routines that work with a bash shell |
| &nbsp; &nbsp; &nbsp; &nbsp;/util | various python routines and utilities |
| &nbsp; &nbsp;/scripy | `scripy` python project scripts |
| &nbsp; &nbsp; &nbsp; &nbsp;/{PROJ} | project directory |
| &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;/plots | plotting scripts |
| &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;/sim_{SIM} | simulation settings |
| results | directory which stores figures and tables created by `scripy` scripts |
| shell | shell scripts and system settings |
| &nbsp; &nbsp;/systems | predefined system settings |

## Installation

Installation of the `arepy` is very simple.
Go to the `arepy` that you cloned from this website and run the installation BASH script:
```
cd $HOME/path/to/arepy
sh install.sh
```

## Documentation and examples

Example scripts are given in subdirectories in corresponding `README.md` files.

## Licensing and contribution
Everybody is welcomed to use this code for private or research purpouse in terms of its license.
Contributions to the code should be consulted with the author.
