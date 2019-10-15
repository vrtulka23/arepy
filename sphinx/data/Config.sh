#!/bin/bash            # this line only there to enable syntax highlighting in this file 

##################################################
#  Enable/Disable compile-time options as needed #
##################################################

#----------------------------- Basic operation mode of code
NTYPES=6
PERIODIC

#----------------------------- MPI/Threading Hybrid
IMPOSE_PINNING

#----------------------------- Mesh Type
VORONOI

#----------------------------- Mesh motion and regularization
REGULARIZE_MESH_CM_DRIFT
REGULARIZE_MESH_CM_DRIFT_USE_SOUNDSPEED
REGULARIZE_MESH_FACE_ANGLE

#----------------------------- Time integration options
TREE_BASED_TIMESTEPS

#----------------------------- Image generation
VORONOI_IMAGES_FOREACHSNAPSHOT
VORONOI_NEW_IMAGE
VORONOI_PROJ_TEMP

#----------------------------- Refinement and derefinement
REFINEMENT_SPLIT_CELLS
REFINEMENT_MERGE_CELLS

#----------------------------- Gravity treatment
SELFGRAVITY
EVALPOTENTIAL

#----------------------------- Things that are always recommended
CHUNKING

#----------------------------- Single/Double Precision
DOUBLEPRECISION=1
DOUBLEPRECISION_FFTW
OUTPUT_IN_DOUBLEPRECISION
INPUT_IN_DOUBLEPRECISION

#----------------------------- Things for special behaviour
VORONOI_DYNAMIC_UPDATE
NO_MPI_IN_PLACE
NO_ISEND_IRECV_IN_DOMAIN
FIX_PATHSCALE_MPI_STATUS_IGNORE_BUG

#----------------------------- Output/Input options
HAVE_HDF5

#----------------------------- Testing and Debugging options
HOST_MEMORY_REPORTING

#----------------------------- SG chemistry options
SGCHEM
SGCHEM_NO_MOLECULES
CHEMISTRYNETWORK=1
JEANS_REFINEMENT=8
CHEM_IMAGE
SGCHEM_CONSTANT_ALPHAB=2.59e-13
SGCHEM_DISABLE_COMPTON_COOLING

#----------------------------- SimpleX - radiative transfer of ionizing radiation on the Delaunay triangulation
SIMPLEX
SX_CHEMISTRY=3
SX_NDIR=84
SX_SOURCES=10
SX_NUM_ROT=5
SX_HYDROGEN_ONLY
SX_DISPLAY_STATS
SX_DISPLAY_TIMERS
SX_IMAGE
SX_IMAGE_ALL

#----------------------------- Healthtest of the machine partition at startup
MAX_VARIATION_TOLERANCE=100

