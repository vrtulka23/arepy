#!/bin/bash

# cluster related settings
RUN_CMD_TERMINAL="mpirun -np $((NUM_NODES*NUM_PROC))"
RUN_CMD_SUBMIT="mpirun"
SUBMIT_CMD="msub"
SUBMIT_INIT="#MSUB -l nodes=${NUM_NODES}:ppn=${NUM_PROC}:${JOB_TYPE}
#MSUB -l walltime=${JOB_WALL_TIME}"
