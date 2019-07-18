# arepy

## Description

`arepy` is a python module that can be used to analyse Arepo output files and snapshots.

It is primarily written in Python (v3.7+), but some parts are written in BASH.

## Installation

Installation of the `arepy` is very simple.
Clone `arepy` into one of the python include directory listed by `echo $PYTHONPATH`.

Alternatively, if you cloned `arepy` into a different directory (e.g. `$HOME/my/python/modules/`) you can add it into the `$PYTHONPATH` by adding the following line in your `.bashrc` profile:
```
export PYTHONPATH=$PYTHONPATH:$HOME/my/python/modules/
```

Then, navigate to the `arepy` directory and run the installation BASH script.
```
cd $HOME/my/python/modules/arepy
sh install.sh
```

This will guide you through the installation and create a `.arepy` directory in the `$HOME` location of the current user. 
This directory includes following files:

| file      | description                                          |
|-----------|------------------------------------------------------|
| settings  | main settings of the environment and directories     |
| projects  | list of projects used for `scripy`                   |
| submitlog | log of the submitted jobs                            | 

## Documentation and examples

Example scripts are given in subdirectories in corresponding `README.md` files.

## Licensing and contribution
Everybody is welcomed to use this code for private or research purpouse in terms of its license.
Contributions to the code should be consulted with the author.
