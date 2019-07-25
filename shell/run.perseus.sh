#!/bin/bash

# cluster related settings
RUN_CMD_TERMINAL="mpirun -np $((NUM_NODES*NUM_PROC))"
RUN_CMD_SUBMIT="mpirun"

JOBID_REGEXP="([0-9]+)"
CANCEL_CMD="canceljob"

SUBMIT_CMD="msub"
submit_init()
{
    echo "#MSUB -l nodes=${1}:ppn=${2}:${3}
#MSUB -l walltime=${4}"
#MSUB -N ${5}"
}
CLEAN_FILES="${JOB_NAME}.e* ${JOB_NAME}.o*"

AREPO_DIR=$arepodir
WORK_DIR=$workdir
