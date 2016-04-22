#!/bin/bash

#Input Variables
Image=$1
Suffix=$2

#Parameters
LxappServer=lxapp-3.sj.us.am.ericsson.se
User=$USER
DestPath=/scratch/testimages/$User
if [ ! -z $Suffix ]; then
    DestImage=$Suffix-$(basename $Image)
else
    DestImage=$(basename $Image)
fi


if [ ! -f $Image ] 
then
    echo "    ERROR: $Image not found"
    exit 1
fi
echo "Copying $Image to $User@$LxappServer:/$DestPath/$DestImage"
scp $Image $User@$LxappServer://$DestPath/$DestImage

