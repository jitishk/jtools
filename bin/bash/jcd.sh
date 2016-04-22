#!/bin/bash
 DestDir=$1
 Pwd=$PWD

IsInRepo=`git rev-parse --is-inside-work-tree`  #Returns true if inside repo

if [ "$IsInRepo" != "true" ]; then
    echo "Not in Repo"
     # echo "$IsInRepo"
    exit 0
fi

echo 'Found repo'

