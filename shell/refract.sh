#!/bin/bash

YEL='\033[0;33m'
NC='\033[0m'

DIR_RUN=$(pwd)                        # directory where we run the script
DIR_MODULE=$(dirname $(dirname $0))   # directory of the arepy module

# go to the correct folder
dirReplace=$DIR_MODULE/python
cd $dirReplace

strFrom="${1}"
strTo="${2}"

# look in the particular files
if [[ -z "${3}" ]]; then
    format="*.py"
else
    format="${3}"
fi

# replace everything
echo -e "${YEL}Changing '${strFrom}' to '${strTo}'${NC}"
found=$(grep -r --include="$format" "${strFrom}" ./)
if [[ ! -z $found ]]; then
    echo -e "${YEL}The following strings will be replaced:${NC}"
    echo "$found"
    read -p $'\e[33mAre you sure (Y/n)?\e[0m ' -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]?$ ]]; then
	echo -e "${YEL}processing...${NC}"
	sedstring="s/${strFrom}/${strTo}/g"
	find ./ -iname "$format" -exec sed -i -e "$sedstring" {} \;
	echo -e "${YEL}done${NC}"
    fi
else
    echo -e "${YEL}No string was found${NC}"
fi

