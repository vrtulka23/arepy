#!/bin/bash

RED='\033[0;31m'               # bash output mark for a red color
GRE='\033[0;32m'           # bash output mark for a green color
YEL='\033[0;33m'           # bash output mark for a yellow color
NC='\033[0m'               # bash output mark to terminate colors

dirModule=$(pwd)
dirArepy="$dirModule/python/arepy"
dirScripy="$dirModule/python/scripy"
fileParameters="$dirModule/settings/parameters.txt"
fileProjects="$dirModule/settings/projects.txt"
fileSubmitLog="$dirModule/settings/submitlog.txt"

echo ""
echo -e "${GRE}Arepy installation${NC}"
echo ""

# Check whether arepy module is within a python path
isPythonDir=0
IFS=':' read -ra ADDR <<< "$PYTHONPATH"
for i in "${ADDR[@]}"; do
    if [ "$i" == "$dirModule/python" ]; then
	isPythonDir=1
	break
    fi
done
if [ "$isPythonDir" == "0" ]; then
    echo -e "${RED}You need to include the following two lines in your .bashrc file:${NC}"
    echo ""
    echo "export PYTHONPATH=\$PYTHONPATH:$dirModule/python
alias arepy='sh $dirModule/shell/run.sh'"
    echo ""
    exit
fi

# Ask for some additional info
echo -e -n "${YEL}Enter your system/machine name (small letters only):${NC} "
read nameSystem
echo ""

fileSystem="${dirModule}/shell/run.${nameSystem}.sh"

# Create corresponding files and directories
echo "runsh=${nameSystem}" > $fileParameters
touch $fileSubmitLog
touch $fileProjects
touch $fileSystem

echo ""
echo "Specific settings for this system/machine can be edited in:"
echo ""
echo "$fileSystem"
echo ""
echo "Arepy installation finished, Bye!"
echo ""
