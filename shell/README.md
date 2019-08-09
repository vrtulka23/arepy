# Arepy help

## Usage

Every option can be triggered by calling `apy` in the commandline.
For example the following arepy call

```bash
apy --init-project myProject
```

will create a new project called 'myProject'.

## General options

Following options can be used system-wide

| Option                       | Description                                  |
|------------------------------|----------------------------------------------|
| --init-project NAME          | initialize scripy project in NAME directory  |  
| --refract OLD NEW [FTYPE]    | replace OLD with NEW code string in scripy and arepy</br> python files or with extension FTYPE |
| --sync                       | synchronize scripy results                   |
|-qa                           | show available resources on the cluster      |
|-ql                           | show queue information on the cluster        |
|-qr                           | show running simulation                      |
|-qh                           | show simulation history log                  |
|-I                            | query for an interactive session             |
|-h                            | show this help                               |

## Project options

Following options can be used only within the project directory tree

| Option                 | Description                                        |
|------------------------|----------------------------------------------------|
| --init-plot NAME       | initialize a new scripy plot called NAME           |
| --init-setup NAME      | initialize a new scripy setup called NAME          |
| --plot NAME [SUBNAME]  | run scripy plot called NAME or its subplot SUBNAME |
| --debug NAME [SUBNAME] | same as --plot, but the plot will be saved to a debug</br> folder instead of a separate time-stamped folder |
| --show NAME [SUBNAME]  | display the last created plot |
| --setup SIM [PART]     | run scripy setup scripts for simulation SIM or its part PART |
|-i                      | creates output/results/scripts directories         |
|-d                      | delete all Arepo runtime files                     |
|-as                     | finds the last created snapshots in all subfolders |

## Simulation options

Following options can be used only in the main directory of a simulation

| Option | Description                                          |
|--------|------------------------------------------------------|
|-si     | submit a job that creates arepo images               |
|-ss     | show simulation stats                                |
|-sr     | submit a restarted job                               |
|-sc     | cancel submited job                                  |
|-s      | submit a new job                                     |
|-ri     | create a custom arepo image                          |
|-rr     | restart job in a terminal                            |
|-r      | run job in a terminal                                |
|-cc     | clean Arepo directory and recompile                  |
|-c      | compile Arepo                                        |
|-ao     | puts output and submit files to an archive directory |
