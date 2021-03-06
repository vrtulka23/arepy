# `arepy`

## Description

`arepy` is a python module that can be used to analyse Arepo output files and snapshots.

It is primarily written in Python (v3.7+), but some parts are written in BASH.

This module requires `numpy`, `scipy` and `h5py` python modules.

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

For more information see the [documentation](https://vrtulka23.github.io/arepy/index.html).

## Licensing and contribution
Everybody is welcomed to use this code for private or research purpouse in terms of its license.
Contributions to the code should be consulted with the author.
