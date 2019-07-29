#!/bin/bash

# cluster related settings
RUN_CMD_TERMINAL="mpirun -np $((NUM_NODES*NUM_PROC))"

CLEAN_FILES="${JOB_NAME}.e* ${JOB_NAME}.o*"

AREPO_DIR=$arepodir
WORK_DIR=$workdir

on_results_sync()
{
    script="rsync -vr --update -e ssh hd_wd148@bwforcluster.bwservices.uni-heidelberg.de:./projects/arepy/results/* $DIR_RESULTS"
    echo -e "${YEL}$script${NC}"; eval "$script"
    
}
