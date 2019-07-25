#!/bin/bash

# cluster related settings
RUN_CMD_TERMINAL="mpirun -np $((NUM_NODES*NUM_PROC))"
RUN_CMD_SUBMIT=""
SUBMIT_CMD=""
SUBMIT_INIT=""

AREPO_DIR=$arepodir
WORK_DIR=$workdir

source $bits/arepo/run.main.sh
