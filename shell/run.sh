#!/bin/bash
 
DIR_RUN=$(pwd)                        # directory where we run the script
DIR_MODULE=$(dirname $(dirname $0))   # directory of the arepy module

DIR_AREPY=$DIR_MODULE/python/arepy    # arepy python scripts
DIR_SCRIPY=$DIR_MODULE/python/scripy  # scripy python scripts
DIR_RESULTS=$DIR_MODULE/results       # directory with scripy results

# Check if in the project directory
DIR_PROJECT="none"
if [ -d "$DIR_SCRIPY/*" ]; then
    for pdir in $(ls -d $DIR_SCRIPY/*)
    do
	pname=$(basename $pdir)
	if [ -f $pdir/__init__.py ]; then
	    psim=$(grep -o '".*"' $pdir/__init__.py | sed 's/"//g')
	    if [[ $DIR_RUN == "$psim"* ]]; then
		DIR_PROJECT="$pname"
	    fi
	fi
    done
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

# Loads global settings
source $DIR_MODULE/shell/run.system.sh

# Call scripts
source $DIR_MODULE/shell/run.main.sh
