import arepy.files.sgchem1              # Specific functions for SGChem primordial
import arepy.files.fiby                 # Specific functions for FiBY snapshots
#import arepy.files.util                 # Routines done with the files

# simulations and snapshot groups
from arepy.files.simulation import *    # Single simulation

# Standard Arepo files
from arepy.files.sink import *          # Arepo sink particles file
from arepy.files.config import *        # Arepo configuration file
from arepy.files.param import *         # Arepo parameter file
from arepy.files.snap import *          # Arepo snapshot file
from arepy.files.image import *         # Arepo image file
from arepy.files.olist import *         # Arepo output list file

# Special Arepo files
from arepy.files.sources import *       # SPRAI test sources file
from arepy.files.runsh import *         # Create a run.sh shell script

# operations on the snapshots
from arepy.files.groups import *        # Group/s of Arepo snapshots
from arepy.files.ics import *           # Create ICs from the grid or from the snapshot
from arepy.files.cut import *           # Create a time/space cut from a simulation snapshot 

# Default settings
default = {
    'snap':{'ftype':'sgchem1','nsub':1,'nproc':1},
}
