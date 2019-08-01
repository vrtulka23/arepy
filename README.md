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
| &nbsp; &nbsp;/arepy | arepy python scripts (main arepy module) |
| &nbsp; &nbsp; &nbsp; &nbsp;/coord | routines for coordinate manipulation |
| &nbsp; &nbsp; &nbsp; &nbsp;/data | routines for dataset manipulation |
| &nbsp; &nbsp; &nbsp; &nbsp;/files | routines that open/edit/wirte Arepo files and simulations |
| &nbsp; &nbsp; &nbsp; &nbsp;/phys | routines with various physical/analytical models and functions |
| &nbsp; &nbsp; &nbsp; &nbsp;/plot | standardized plotting routines |
| &nbsp; &nbsp; &nbsp; &nbsp;/scripy | `scripy` classes and templates |
| &nbsp; &nbsp; &nbsp; &nbsp;/shell | python routines that work with a bash shell |
| &nbsp; &nbsp; &nbsp; &nbsp;/util | various python routines and utilities |
| &nbsp; &nbsp;/scripy/{PROJECT} | project directory |
| &nbsp; &nbsp; &nbsp; &nbsp;/plots/{PLOT} | plotting scripts |
| &nbsp; &nbsp; &nbsp; &nbsp;/setups/{SETUP} | simulation setup scripts  |
| results | directory which stores figures and tables created by `scripy` scripts |
| shell | shell scripts and system settings |
| &nbsp; &nbsp;/systems | predefined system settings |

## Installation

Installation of the `arepy` is very simple!

Go to the main `arepy` directory that you cloned from this website and run the installation BASH script:
```
cd $HOME/path/to/arepy
sh install.sh
```

The installation script will ask you to include `python/` directory into your local $PYTHONPATH and also to create an alias for the `arepy` bash script `shell/run.sh`.

In the next step you will have to choose system settings. You can either choose existing settings by inputing one of the system names in `shell/systems/run.{SYSTEM_NAME}.sh` or create a new one by putting your own name.

After this the `arepy` python module can be included in any python script and you will be also able to use `arepy` shell scripts from your terminal.

## Documentation and examples

Example scripts are given in subdirectories in corresponding `README.md` files.

## Licensing and contribution
Everybody is welcomed to use this code for private or research purpouse in terms of its license.
Contributions to the code should be consulted with the author.
