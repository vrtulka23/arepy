#!/bin/bash

# cluster related settings
RUN_CMD_TERMINAL="mpirun -np $((NUM_NODES*NUM_PROC))"
RUN_CMD_DEBUG="mpirun -gdb -n $((NUM_NODES*NUM_PROC))"
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

on_inter_run()
{
    INTER_CMD="msub -I -V -X -l nodes=${nodes}:ppn=${ppn}:${type},walltime=${walltime}"
}

on_queue_avail()
{
    echo -e "\033[0;33mStandard\033[0m";
    printf "$(showbf -f standard)\n"
    echo -e "\033[0;33mBest\033[0m";
    printf "$(showbf -f best)\n"
    echo -e "\033[0;33mFat\033[0m";
    printf "$(showbf -f fat)\n"
    echo -e "\033[0;33mFat-ivy\033[0m";
    printf "$(showbf -f fat-ivy)\n"
    echo -e "\033[0;33mMic\033[0m";
    printf "$(showbf -f mic)\n"
    echo -e "\033[0;33mGPU\033[0m";
    printf "$(showbf -f gpu)\n"
}

on_queue_list()
{
    showq
}

on_load_python()
{
    conda activate py37
}
