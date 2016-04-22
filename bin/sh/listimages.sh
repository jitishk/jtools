#!/bin/bash

User=$USER
ScratchNum=9
ProjectNum=9
ErrorStr="    %ERROR:"
ScratchDir=/scratch/$ScratchNum/$User
ProjectDir=/project/swbuild$ProjectNum/$User
PresentWorkingDir=`pwd`


usage () {
    ScriptName=$(basename "$0" .sh)
    echo "Display directory contents of /scratch/testimages/$User"
    echo "Usage: $ScriptName [-h|-lah]"
}


if [ ! -z $1 ];
then
    if [ $1 = "-h" ] || [ $1 = "--help" ] || [ $# -gt 1 ];
    then
        usage
        exit 0
    fi
fi

ssh $User@lxapp-3.sj.us.am.ericsson.se "ls /scratch/testimages/$User/*.tar.gz"

