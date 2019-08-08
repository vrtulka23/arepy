#!/bin/bash

RED='\033[0;31m'               # bash output mark for a red color
GRE='\033[0;32m'           # bash output mark for a green color
YEL='\033[0;33m'           # bash output mark for a yellow color
NC='\033[0m'               # bash output mark to terminate colors

dirModule=$(pwd)
dirArepy="$dirModule/python/arepy"
dirScripy="$dirModule/python/scripy"
fileSubmitLog="$dirModule/.submitlog"

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
alias apy='sh $dirModule/shell/run.sh'"
    echo ""
    echo -e "${RED}After that restart this installation script for further steps.${NC}"
    exit
fi

# Ask for some additional info
echo -e -n "${YEL}Enter your system/machine name (small letters only):${NC}\n  "
read nameSystem
echo ""

fileSystemTemplate="${dirModule}/shell/systems/run.${nameSystem}.sh"
fileSystem=$dirModule/shell/run.system.sh
if [ -f $fileSystemTemplate ] && [ ! -f $fileSystem ]; then
    cp $fileSystemTemplate $fileSystem
else
    touch $fileSystem
fi

# Create submit log file
touch $fileSubmitLog

echo -e "${YEL}Specific settings for this system/machine can be edited in:${NC}"
echo "  $fileSystem"
echo ""
echo -e "${YEL}More advanced arepy commands require Arepo source code in the following directory:${NC}"
echo "  $dirModule/arepo/(SourceCode)"
echo ""
echo -e "${GRE}Arepy installation finished, Bye!${NC}"
echo ""
