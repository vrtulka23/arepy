#!/bin/bash
# The following system configuration is loaded by the 'run.sh' script and overrides it defaults
# You can tailor the following commands at your will


# Custom Arepo directory (if not set, Arepo is assumed to be in the main arepy directory)
#DIR_AREPO=/my/path/to/arepo


# Commands used to run Arepo in parallel (mpirun,mpiexec,..)
RUN_CMD_TERMINAL="mpirun -np $((NUM_NODES*NUM_PROC))"
RUN_CMD_SUBMIT="mpirun"


# Command that submits a job to the queue (msub, qsub,...)
SUBMIT_CMD="msub"


# Regular expression that finds the job ID in the submission message
JOBID_REGEXP="([0-9]+)"


# Command that cancels the job
CANCEL_CMD="canceljob"


# Initial settings of the submit job script
submit_init()
{
    echo "#MSUB -l nodes=${1}:ppn=${2}:${3}
#MSUB -l walltime=${4}"
#MSUB -N ${5}"
}


# Files that will be cleaned besides the regular files (apy -d)
CLEAN_FILES="${JOB_NAME}.e* ${JOB_NAME}.o*"


# Custom that calls an interactive session (apy -I)
on_inter_run()
{
    INTER_CMD="msub -I -V -X -l nodes=${nodes}:ppn=${ppn}:${type},walltime=${walltime}"
}


# Custom that show available queues (apy -qa)
on_queue_avail()
{
    echo -e "\033[0;33mStandard\033[0m";
    printf "$(showbf -f standard)\n"
    echo -e "\033[0;33mBest\033[0m";
    printf "$(showbf -f best)\n"
}


# Command that shows a queue of the user (apy -q)
on_queue_list()
{
    showq
}


# Custom synchronization script for the results (apy --sync)
on_results_sync()
{
    script="rsync -vr --update --exclude='*.npy' -e ssh user@host:./arepy/results/* $DIR_RESULTS"
    echo -e "${YEL}$script${NC}"; eval "$script"
}
