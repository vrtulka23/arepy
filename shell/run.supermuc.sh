#!/bin/bash

# cluster related settings
WORK_DIR=$workdir
AREPO_DIR=$arepodir
JOB_NAME="${PWD##*/}"
RUN_CMD_TERMINAL="mpirun -np $((NUM_NODES*NUM_PROC))"
RUN_CMD_SUBMIT="mpiexec"

JOBID_REGEXP="srv[0-9]+-ib[.0-9]+"
CANCEL_CMD="llcancel"

SUBMIT_CMD="llsubmit"
SUBMIT_INIT="#!/bin/bash
#@ job_type = MPICH
#@ class = ${JOB_TYPE}
#@ node = ${NUM_NODES}
#@ tasks_per_node = ${NUM_PROC}
#@ wall_clock_limit = ${JOB_WALL_TIME}
#@ job_name = ${JOB_NAME}
#@ island_count = 1
#@ network.MPI = sn_all,not_shared,us
#@ output = submit.out
#@ error = submit.err
#@ notification = never
#@ energy_policy_tag = my_energy_tag_33
#@ minimize_time_to_solution = yes
#@ queue
. /etc/profile
. /etc/profile.d/modules.sh
module load fftw
module load gsl
module load hdf5
module load hwloc
module unload mpi.ibm
module unload mpi.ompi
module load mpi.intel
module unload mpi.intel intel mkl
module load mkl/11.3 intel/16.0 mpi.intel/5.1
export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:${library}"

on_submit_avail()
{
    echo -e "\033[0;33mFat\033[0m";
    llq -c fat | tail -1
    echo -e "\033[0;33mTest\033[0m";
    llq -c test | tail -1
}

on_submit_queue()
{
    llq -u di57jir2
}