#!/bin/bash            # this line only there to enable syntax highlighting in this file

##################################################
#  Enable/Disable compile-time options as needed #
##################################################


#--------------------------------------- Basic operation mode of code
NTYPES=6                       # number of particle types
PERIODIC

#----------------------------------------MPI/Threading Hybrid
IMPOSE_PINNING

#--------------------------------------- Mesh Type
VORONOI

#--------------------------------------- Mesh motion and regularization
REGULARIZE_MESH_CM_DRIFT
REGULARIZE_MESH_CM_DRIFT_USE_SOUNDSPEED
REGULARIZE_MESH_FACE_ANGLE

#--------------------------------------- Time integration options
TREE_BASED_TIMESTEPS     # non-local timestep criterion (take 'signal speed' into account)

#--------------------------------------- Image generation
VORONOI_IMAGES_FOREACHSNAPSHOT
VORONOI_NEW_IMAGE
VORONOI_PROJ_TEMP                        # project T instead of u

#--------------------------------------- Refinement and derefinement
REFINEMENT_SPLIT_CELLS
REFINEMENT_MERGE_CELLS

#--------------------------------------- Gravity treatment
SELFGRAVITY                   # switch on for self-gravity     
EVALPOTENTIAL                 # computes gravitational potential

#--------------------------------------- Things that are always recommended
CHUNKING                 # will calculated the gravity force in interleaved blocks. This can reduce imbalances in case multiple iterations due to insufficient buffer size need to be done
                          

#---------------------------------------- Single/Double Precision
DOUBLEPRECISION=1
DOUBLEPRECISION_FFTW
OUTPUT_IN_DOUBLEPRECISION                # snapshot files will be written in double precision
INPUT_IN_DOUBLEPRECISION                 # initial conditions are in double precision

#-------------------------------------------- Things for special behaviour
VORONOI_DYNAMIC_UPDATE          # keeps track of mesh connectivity, which speeds up mesh construction
NO_MPI_IN_PLACE
NO_ISEND_IRECV_IN_DOMAIN
FIX_PATHSCALE_MPI_STATUS_IGNORE_BUG

#--------------------------------------- Output/Input options
HAVE_HDF5                     # needed when HDF5 I/O support is desired

#--------------------------------------- Testing and Debugging options
HOST_MEMORY_REPORTING         # reports after start-up the available system memory by analyzing /proc/meminfo

#--------------------------------------- Healthtest of the machine partition at startup
#MAX_VARIATION_TOLERANCE=8

#-------------------------------------- SG chemistry options
SGCHEM
CHEMISTRYNETWORK=1
JEANS_REFINEMENT=8
#STATIC_CHEMISTRY_TEST
#ADVECTION_ONLY
CHEM_IMAGE
#ABHE
#SG_HEADER_FLAG
#DEBUG_EVOLVE
#DEBUG_RATE_EQ
SGCHEM_NO_MOLECULES

SGCHEM_CONSTANT_ALPHAB=2.59e-13        # this options sets a fixed alpha_B parameter instead of temperature dependant 
SGCHEM_DISABLE_COMPTON_COOLING         # sets compton cooling rate to zero

#--------------------------------------- SimpleX - radiative transfer of ionizing radiation on the Delaunay triangulation           

SIMPLEX                        # SimpleX main switch

SX_CHEMISTRY=3                 # chemistry network: 3) SGChem 4) FiBY
SX_NDIR=84                     # number of directional bins used

SX_SOURCES=10                   # source of radiation 4 = stars; 5 = sinks; 10> = test sources

SX_NUM_ROT=5                   # number of direction base rotations per RT (0 = static base)

#SX_RECOMBINE

SX_HYDROGEN_ONLY                # switch off helium mass fraction in Arepo or SGChem
SX_DISPLAY_STATS                # display statistics about radiation transfer step
SX_DISPLAY_TIMERS               # display basic timers at the end of each run
#SX_DISPLAY_TIMERS_SITE         # display advanced timers for the site
#SX_DISPLAY_MEMORY              # display memory statistics
SX_OUTPUT_IMAGE                 # produce Arepo images of RIH and HRIH (slices and projections)
SX_OUTPUT_IMAGE_ALL             # produce multi-dim Arepo image with all ionization rates (slices only)
SX_OUTPUT_FLUX                  # for each cell and frequency output fluxes 

#SX_RADIATION_PRESSURE          # switch for the radiation pressure

#GAMMA=1.00001                  # standard GAMMA parameter used by Arepo and SGChem

#------ OTHER

MAX_VARIATION_TOLERANCE=100
