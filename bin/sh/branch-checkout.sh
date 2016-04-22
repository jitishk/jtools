#!/bin/sh

#global variables
CMD_PATH=/tools/swdev/bin
SRC_PATH=/project/swbuild1/$USER
TREES_PATH=~/trees


if [ $# -ne 3 ]; then
    echo "usage: $SCRIPTNAME branch-name module dir-name "
    echo "    branch-name     : name of branch (e.g. swfeature_int)"
    echo "    module          : name of module (e.g. se_full|pcref|plat|se_all)"
    echo "    dir-name        : name of directory for src (e.g. sfi_158980)"
    exit 2
fi

Branch=$1
Module=$2
BranchDir=$3

echo "Creating new dir branch as $SRC_PATH/$BranchDir/... "
cd $SRC_PATH
if [ -d $BranchDir ]; then
    echo "    %ERROR: Directory $SRC_PATH/$BranchDir exists"
    exit 1
fi
mkdir $BranchDir
if [ ! -d $BranchDir ]; then
    echo "    %ERROR: Could not create $SRC_PATH/$BranchDir"
    exit 1
fi
echo "    done"

echo "Linking $SRC_PATH/$BranchDir/ to $TREES_PATH/$BranchDir... "
rm -rf $TREES_PATH/$BranchDir
ln -sf $SRC_PATH/$BranchDir/ $TREES_PATH/$BranchDir
echo "    done"

#
echo "Checking out branch $Branch @ $BranchDir (output in cvs.co)... "
cd $SRC_PATH/$BranchDir/
$CMD_PATH/cvsm -Q co -r$1 $Module >| cvs.co
echo "    done"
