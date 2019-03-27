#!/bin/bash

YEL='\033[0;33m'
NC='\033[0m'

if [[ -z "${3}" ]]; then
    format="*.py"
else
    format="${3}"
fi

echo -e "${YEL}Changing '${1}' to '${2}'${NC}"
found=$(grep -r --include="$format" "${1}" ./)
if [[ ! -z $found ]]; then
    echo -e "${YEL}The following strings will be replaced:${NC}"
    echo "$found"
    read -p $'\e[33mAre you sure (Y/n)?\e[0m ' -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]?$ ]]; then
	echo -e "${YEL}processing...${NC}"
	sedstring="s/$1/$2/g"
	find ./ -iname "$format" -exec sed -i -e "$sedstring" {} \;
	echo -e "${YEL}done${NC}"
    fi
else
    echo -e "${YEL}No string was found${NC}"
fi

