# Arepy help

## Usage

Every option can be triggered by calling `apy` in the commandline

## General options

Following options can be used system-wide

```bash
       --init-project <name>         initialize scripy project directory
       --sync                        synchronize scripy results
       --refract <old> <new> [<ft>]  replace <old> with <new> code in scripy and arepy python scripts or with extension <ft>
-sa  | --submit-avail                show available resources on the cluster
-sq  | --submit-queue                show queue information on the cluster
-sl  | --submit-log                  show simulation history log
-slr | --submit-log-running          show running simulation
-I   | --inter-sess                  query for an interactive session
-h   | --help                        show this help
```

## Project options

Following options can be used only within the project directory tree

```bash
       --init-plot <name>            initialize a new scripy plot
       --init-setup <name>           initialize a new setup
       --plot <script>               run scripy plot scripts
       --setup <sim> [<part>]        run scripy setup scripts
-i   | --initialize                  creates output/results/scripts directories
-d   | --clean-dir                   delete all Arepo runtime files
-as  | --analyze-snaps               finds the last created snapshots in all subfolders
```

## Simulation options

Following options can be used only in the main simulation directory tree

```bash
-si  | --submit-image                submit a job that creates arepo images
-ss  | --submit-stats                show simulation stats
-sr  | --submit-restart              submit a restarted job
-sc  | --submit-cancel               cancel submited job
-s   | --submit                      submit a new job
-ri  | --terminal-image              create a custom arepo image
-rr  | --terminal-restart            restart job in a terminal
-r   | --terminal                    run job in a terminal
-cc  | --compile-clean               clean Arepo directory and recompile
-c   | --compile                     compile Arep
-ao  | --archive-output              puts output and submit files to an archive directory
```
