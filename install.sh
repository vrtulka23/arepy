#!/bin/bash

RED='\e[31m'               # bash output mark for a red color
GRE='\033[0;32m'           # bash output mark for a green color
YEL='\033[0;33m'           # bash output mark for a yellow color
NC='\033[0m'               # bash output mark to terminate colors

dirInit="$HOME/.arepyTest"
dirPython=$(dirname $(pwd))
dirScripy="$dirPython/scripyTest"
fileSettings="$dirInit/settings"
fileProjects="$dirInit/projects"
fileSubmitLog="$dirInit/submitlog"

echo ""
echo -e "${GRE}Arepy installation${NC}"
echo ""

mkdir $dirInit
touch ~/.arepy/submitlog
echo "Settings directory: $dirInit"
echo ""

echo -e -n "${YEL}Enter your system/machine name (small letters only):${NC} "
read nameSystem
echo -e -n "${YEL}Enter path to the results directory:${NC} "
read dirResults

echo "runsh=${nameSystem}
arepy=$dirPython/arepy
scripy=$dirScripy
results=$dirResults" > $fileSettings
mkdir $dirResults
mkdir $dirScripy

echo -e -n "${YEL}Enter scripy project name (small letters only):${NC} "
read nameProject
echo -e -n "${YEL}Enter scripy project directory:${NC} "
read dirProject
echo ""

echo "$nameProject=$dirProject" > $fileProjects
mkdir $dirProject
dirScripyProject="$dirScripy/$nameProject"
mkdir $dirScripyProject

echo "Settings created:"
echo "$fileSettings"
echo "$fileProjects"
echo "$fileSubmitLog"
echo ""
echo "Directories created:"
echo "$dirResults"
echo "$dirProject"
echo "$dirScripy"
echo "$dirScripyProject"

echo ""
echo "Arepy installation finished, Bye!"
echo ""
