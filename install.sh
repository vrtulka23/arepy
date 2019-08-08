#!/bin/bash

RED='\033[0;31m'               # bash output mark for a red color
GRE='\033[0;32m'           # bash output mark for a green color
YEL='\033[0;33m'           # bash output mark for a yellow color
NC='\033[0m'               # bash output mark to terminate colors

DIR_PWD=$(pwd)

echo ""
echo -e "${GRE}Arepy installation${NC}"
echo ""

# Check whether arepy module is within a python path
isPythonDir=0
IFS=':' read -ra ADDR <<< "$PYTHONPATH"
for i in "${ADDR[@]}"; do
    if [ "$i" == "$DIR_PWD/python" ]; then
	isPythonDir=1
	break
    fi
done
if [ "$isPythonDir" == "0" ]; then
    echo -e "${RED}Step 1) You need to include the following two lines in your .bashrc file:${NC}"
    echo ""
    echo "export PYTHONPATH=\$PYTHONPATH:$DIR_PWD/python
alias apy='sh $DIR_PWD/shell/run.sh'"
    echo ""
    echo -e "${RED}After that restart this installation script for further steps.${NC}"
    exit
else
    echo -e "${YEL}Step 1) Python path and aliases are included in .bashrc${NC}"
    echo ""
fi

# Ask for some additional info
echo -e -n "${YEL}Step 2) Enter your system/machine name (small letters only):${NC}\n  "
read nameSystem
echo ""

fileSystemTemplate="${DIR_PWD}/shell/systems/run.${nameSystem}.sh"
fileSystem=$DIR_PWD/shell/run.system.sh
if [ -f $fileSystemTemplate ] && [ ! -f $fileSystem ]; then
    cp $fileSystemTemplate $fileSystem
else
    touch $fileSystem
fi

# Create submit log file
touch "$DIR_PWD/.submitlog"

echo -e "${YEL}Step 3) Specific settings for this system/machine can be edited in:${NC}"
echo "  $fileSystem"
echo ""
echo -e "${YEL}Step 4) More advanced arepy commands require Arepo source code in the following directory:${NC}"
echo "  $DIR_PWD/arepo/(SourceCode)"
echo ""
echo -e "${GRE}Arepy installation finished, Bye!${NC}"
echo ""
