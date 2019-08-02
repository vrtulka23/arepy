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
| --refract OLD NEW [FTYPE]    | replace OLD with NEW code string in scripy and arepy python files or with extension FTYPE |
| --sync                       | synchronize scripy results                   |
|-sa                           | show available resources on the cluster      |
|-sq                           | show queue information on the cluster        |
|-sl                           | show simulation history log                  |
|-slr                          | show running simulation                      |
|-I                            | query for an interactive session             |
|-h                            | show this help                               |

## Project options

Following options can be used only within the project directory tree

| Option                | Description                                        |
|-----------------------|----------------------------------------------------|
| --init-plot NAME      | initialize a new scripy plot called NAME           |
| --init-setup NAME     | initialize a new scripy setup called NAME          |
| --plot NAME [SUBNAME] | run scripy plot called NAME or its subplot SUBNAME |
| --setup SIM [PART]    | run scripy setup scripts for simulation SIM or its part PART |
|-i                     | creates output/results/scripts directories         |
|-d                     | delete all Arepo runtime files                     |
|-as                    | finds the last created snapshots in all subfolders |

## Simulation options

Following options can be used only in the main simulation directory tree

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
|-c      | compile Arep                                         |
|-ao     | puts output and submit files to an archive directory |