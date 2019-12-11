#!/bin/bash

# cluster related settings
RUN_CMD_TERMINAL="mpirun -np $((NUM_NODES*NUM_PROC))"
RUN_CMD_SUBMIT="srun --mpi=pmi2"

JOBID_REGEXP="([0-9]+)"
CANCEL_CMD="scancel"

SUBMIT_CMD="sbatch"
SUBMIT_INIT="
#SBATCH -n $((NUM_NODES*NUM_PROC))
#SBATCH --ntasks-per-node=${NUM_PROC}
#SBATCH -p ${JOB_TYPE}
#SBATCH -A bw16L013
"
CLEAN_FILES="slurm*"

INTER_CMD="srun -N 2 --ntasks-per-node=16 --pty bash"

AREPO_DIR=$arepodir
WORK_DIR=$workdir

on_queue_avail()
{
    sinfo
}

on_queue_list()
{
    squeue
}
