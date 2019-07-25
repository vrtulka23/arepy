#!/bin/bash
 
DIR_RUN=$(pwd)                        # directory where we run the script
DIR_MODULE=$(dirname $(dirname $0))   # directory of the arepy module

DIR_SETTINGS=$DIR_MODULE/settings     # directory with arepy settings
DIR_AREPY=$DIR_MODULE/python/arepy    # arepy python scripts
DIR_SCRIPY=$DIR_MODULE/python/scripy  # scripy python scripts
DIR_RESULTS=$DIR_MODULE/results       # directory with scripy results

# Check if in the project directory
DIR_PROJECT="none"
while IFS='=' read -r pname pdir
do 
    if [[ $DIR_RUN == "$pdir"* ]]; then
	DIR_PROJECT="$pname"
    fi
done < $DIR_SETTINGS/projects.txt

# Load local settings
while [ "$DIR_RUN" != "/" ]
do
    if [ -e "$DIR_RUN/run.sh" ] # load settings from the current dir
    then
	source $DIR_RUN/run.sh
	break
    else                            # look in a parent directory
	DIR_RUN=$(dirname $DIR_RUN)
    fi
done

# Loads global settings
if [ -f $DIR_SETTINGS/parameters.txt ]; then
    MACHINE=$(grep "runsh=" $DIR_SETTINGS/parameters.txt | sed 's/runsh=//')
    scriptDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
    source "${DIR_MODULE}/shell/run.${MACHINE}.sh"
else
    MACHINE="no-machine"
    echo -e "${RED}Could not find settings for this machine! Check if the machine name in ~/.runsh is set correctly.${NC}"
fi

# Call scripts
source $DIR_MODULE/shell/run.main.sh
