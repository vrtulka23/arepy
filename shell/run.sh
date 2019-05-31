#!/bin/bash
 
DIR_RUN=$(pwd)

# Check if in the project directory
DIR_PROJECT="none"
while IFS='=' read -r pname pdir
do 
    if [[ $DIR_RUN == "$pdir"* ]]; then
	DIR_PROJECT="$pname"
    fi
done < ~/.arepy/projects

# Loads global settings
DIR_AREPY=$(grep "arepy=" ~/.arepy/settings | sed 's/arepy=//')
DIR_SCRIPY=$(grep "scripy=" ~/.arepy/settings | sed 's/scripy=//')
DIR_RESULTS=$(grep "results=" ~/.arepy/settings | sed 's/results=//')
if [ -f ~/.arepy/settings ]; then
    MACHINE=$(grep "runsh=" ~/.arepy/settings | sed 's/runsh=//')
    scriptDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
    source "${DIR_AREPY}/shell/run.${MACHINE}.sh"
else
    MACHINE="no-machine"
    echo -e "${RED}Could not find settings for this machine! Check if the machine name in ~/.runsh is set correctly.${NC}"
fi

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

# Call scripts
source $DIR_AREPY/shell/run.main.sh
