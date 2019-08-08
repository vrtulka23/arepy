#!/bin/bash

RED='\033[0;31m'               # bash output mark for a red color
GRE='\033[0;32m'           # bash output mark for a green color
YEL='\033[0;33m'           # bash output mark for a yellow color
NC='\033[0m'               # bash output mark to terminate colors

DIR_PWD=$(pwd)
DIR_PYTHON=$DIR_PWD/python

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
echo -e "${YEL}Step 1) Setting arepy python path and alias${NC}"
echo ""
if [ "$isPythonDir" == "0" ]; then
    echo -e "  ${RED}You need to include the following two lines in your .bashrc file:"
    echo ""
    echo "  export PYTHONPATH=\$PYTHONPATH:$DIR_PYTHON"
    echo "  alias apy='sh $DIR_PWD/shell/run.sh'"
    echo ""
    echo -e "  ${RED}After that restart this installation script for further steps.${NC}"
    exit
else
    echo "  Settings saved to .bashrc:"
    echo ""
    echo "  export PYTHONPATH=\$PYTHONPATH:$DIR_PYTHON"
    echo "  alias apy='sh $DIR_PWD/shell/run.sh'"
fi
echo ""

# Ask for some additional info
echo -e -n "${YEL}Step 2) Enter your system/machine name (small letters only):${NC}\n\n  "
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

echo -e "${YEL}Step 3) Setting up Arepo${NC}"
echo ""
echo "  For more advanced arepy commands you need to clone arepo source code to:"
echo "  $DIR_PWD/arepo/(SourceCode)"
echo ""
echo "  Alternatively, you can add your arepo path to the 'shell/run.system.sh' script as:"
echo "  DIR_AREPO=/your/favourite/path/to/arepo"
echo ""
echo -e "${GRE}Arepy installation finished, Bye!${NC}"
echo ""
