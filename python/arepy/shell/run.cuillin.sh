#!/bin/bash

# cluster related settings
RUN_CMD_TERMINAL="mpirun -np $((NUM_NODES*NUM_PROC))"
RUN_CMD_SUBMIT="mpirun -np $((NUM_NODES*NUM_PROC))"

JOBID_REGEXP="([0-9]+)"
CANCEL_CMD="scancel"

SUBMIT_CMD="sbatch"
SUBMIT_INIT="
#SBATCH --time=00:30:00
#SBATCH --ntasks=$((NUM_NODES*NUM_PROC))
#SBATCH --output=submit.out
#SBATCH --mem-per-cpu=4G

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/lib/lib/
export PATH=$PATH:$HOME/lib/bin/
"
CLEAN_FILES="slurm*"

AREPO_DIR=$arepodir
WORK_DIR=$workdir

on_submit_avail()
{
    sinfo
}

on_submit_queue()
{
    squeue
}
