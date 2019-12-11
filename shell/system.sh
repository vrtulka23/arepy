#!/bin/bash

DIR_AREPO=/home/hd/hd_hd/hd_wd148/projects/arepo

# cluster related settings
RUN_CMD_TERMINAL="mpirun -np $((NUM_NODES*NUM_PROC))"
RUN_CMD_SUBMIT="srun --mpi=pmi2"

JOBID_REGEXP="([0-9]+)"
CANCEL_CMD="scancel"

SUBMIT_CMD="sbatch"
submit_init()
{
    echo "
#SBATCH -n $((${1}*${2}))
#SBATCH --ntasks-per-node=${2}
#SBATCH -p ${3}
#SBATCH -A bw16L013
"
}
CLEAN_FILES="slurm*"

INTER_CMD="srun -N 2 --ntasks-per-node=16 --pty bash"


on_queue_avail()
{
    sinfo
}

on_queue_list()
{
    squeue
}


# Custom that calls an interactive session (apy -I)
on_inter_run()
{
    INTER_CMD="srun -N ${nodes} --ntasks-per-node=${ppn} --pty bash"
}

