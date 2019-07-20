#!/bin/bash

RED='\033[0;31m'               # bash output mark for a red color
GRE='\033[0;32m'           # bash output mark for a green color
YEL='\033[0;33m'           # bash output mark for a yellow color
NC='\033[0m'               # bash output mark to terminate colors

dirInit="$HOME/.arepy"
dirCurrent=$(dirname $(pwd))
dirScripy="$dirCurrent/scripy"
fileSettings="$dirInit/settings"
fileProjects="$dirInit/projects"
fileSubmitLog="$dirInit/submitlog"

echo ""
echo -e "${GRE}Arepy installation${NC}"
echo ""

# Check whether arepy module is within a python path
isPythonDir=0
IFS=':' read -ra ADDR <<< "$PYTHONPATH"
for i in "${ADDR[@]}"; do
    if [ "$i" == "$dirCurrent" ]; then
	isPythonDir=1
	break
    fi
done
if [ "$isPythonDir" == "0" ]; then
    echo -e "${RED}Arepy module has to be in a python module directory!${NC}"
    echo "Current directory: $dirCurrent"
    echo "\$PYTHONPATH: $PYTHONPATH"
    echo ""
    exit
fi

# Show some information
echo "Current directory: $dirCurrent"
echo ""

# Ask for some additional info
echo -e -n "${YEL}Enter your system/machine name (small letters only):${NC} "
read nameSystem
echo -e -n "${YEL}Enter path to the results directory:${NC} "
read dirResults
echo ""

# Create corresponding files and directories
mkdir $dirInit
touch ~/.arepy/submitlog
echo "runsh=${nameSystem}
arepy=$dirCurrent/arepy
scripy=$dirScripy
results=$dirResults" > $fileSettings
mkdir $dirResults
mkdir $dirScripy
touch $fileProjects

# Display a summary
echo "Settings files:"
echo "$fileSettings"
echo "$fileProjects"
echo "$fileSubmitLog"
echo ""
echo "Scripy directories:"
echo "$dirResults"
echo "$dirScripy"

echo ""
echo "Arepy installation finished, Bye!"
echo ""
