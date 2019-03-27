#!/bin/bash

# Other options
ANALYZE_DIR="none"

# Cluster option
NUM_NODES=0                # number of nodes
NUM_PROC=0                 # number of processors per node
JOB_WALL_TIME="0"          # wall time of the run
JOB_TYPE="no-queue"        # type of nodes
FLAGS_RUN=""               # Arepo run flags
FLAGS_RESTART="1"          # Arepo restart flags

# Arepo Images
IMAGE_NODES=0
IMAGE_PROC=0
IMAGE_WALLTIME="0"
IMAGE_TYPE="no-queue"
IMAGE_FLAGS=(0 100 0.149850 0.150150 0.149850 0.150150 0.149850 0.150150)

source ~/.arepy/run.sh

