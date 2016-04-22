#!/bin/bash

# TODO
# 1. jcscope . /scratch/9/ejitkol/evs.git overrides a previous cscope files
# based on another directory
#
# 1. jcscope evs.git mpls. Find a better way to get ccscopeSubDir. try 
# find -type d

User=$USER
ScratchNum=9
ProjectNum=9
ErrorStr="    %ERROR:"
ScratchDir=/scratch/$ScratchNum/$User
ProjectDir=/project/swbuild$ProjectNum/$User
PresentWorkingDir=`pwd`
ScriptName=$(basename "$0" .sh)


usage () {
    echo "Usage: $ScriptName <tree-name> <sub-directory-name>"
    echo "       $ScriptName <absolute-source-path> [absolute-dest-path]"
}

jscope_set_cscope_sub_directory () {
    case $1 in
        "")
            CscopeSubDir=.
            ;;
        rib)
            CscopeSubDir=pkt/sw/se/xc/bsd/routing/rib
            ;;
        routing)
            CscopeSubDir=pkt/sw/se/xc/bsd/routing
            ;;
        *)
            echo "$ErrorStr Unknown sub directory $1" 2>&1
            exit 1
            ;;
    esac
}

if [ $# -eq 0 ] || [ $1 = "-h" ] || [ $1 = "--help" ] || [ $# -lt 1 ];
then
    usage
    exit 0
fi

# Check is provided source directory is absolute. If it is, accept it as is and
# read the optional second parameter as the destination directory to store the
# cscope files.
# Else add the project and scratch directory suffixes to the source and
# destination directories, and determine the cscope sub directory.
if [[ $1 = /* ]] || [ $1 = . ];
then
    SourceRootDir=$1
    DestDir=$2
    CscopeSubDir=
else
    SourceRootDir=$ProjectDir/$1
    DestDir=$ScratchDir/$1
    # If destination directory does not exist, create one in scratch space
    # based on the source tree directory.
    if [ ! -d $DestDir ];
    then
        mkdir $DestDir
    fi
    CscopeSubDirName=$2
    jscope_set_cscope_sub_directory $CscopeSubDirName
fi

echo "Src $SourceRootDir"
echo "Dst $DestDir"
echo "Sub $CscopeSubDir"

# Sanity check directories
echo "Sanity check for directories... " 
if [ ! -d $SourceRootDir ];
then
    echo "$ErrorStr Invalid Source Directory $SourceRootDir" 2>&1
    exit 1
fi
if [ $DestDir ] && [ ! -d $DestDir ];
then
    echo "$ErrorStr Invalid Desination Directory $DestDir" 2>&1
    exit 1
fi
if [ $CscopeSubDir ] && [ ! -d $SourceRootDir/$CscopeSubDir ];
then
    echo "$ErrorStr Invalid Cscope Directory $SourceRootDir/$CscopeSubDir" 2>&1
    exit 1
fi
echo "Done"

echo "Removing previous cscope files, if any..."
rm -rf $SourceRootDir/$CscopeSubDir/cscope.*
rm -rf $DestDir/cscope*$CscopeSubDirName.*
echo "Done"

# Creating cscope database
cd $SourceRootDir/$CscopeSubDir
echo "collecting *.[chs] files..."
find . -name "*.[chsC]" -print > cscope.files
echo "    Done"

echo "collecting .inc files..."
find . -name "*.inc" -print >> cscope.files
echo "    Done"

echo "collecting .txt files..."
find . -name "*.txt" -print >> cscope.files
echo "    Done"

echo "collecting .dll files..."
find . -name "*.ddl" -print >> cscope.files
echo "    Done"

echo "collecting .py files..."
find . -name "*.py" -print >> cscope.files
echo "    Done"

echo "collecting .cc files..."
find . -name "*.cc" -print >> cscope.files
echo "    Done"

echo "collecting .mk files..."
find . -name "*.mk" -print >> cscope.files
echo "    Done"

echo "collecting .mk files..."
find . -name "*.i" -print >> cscope.files
echo "    Done"

echo "collecting make files..."
find . -name "Makefile" -print >> cscope.files
echo "    Done"
 
echo "collecting .java files..."
find . -name "*.java" -print >> cscope.files
echo "    Done"
 
echo "building database..."

alias cscope=`which cscope`
cscope -bq
# /app/cscope/15.8a/LMWP3/bin/cscope -bq
echo "    Done"

if [ ! $DestDir ]; then
    # If no destination has been provided, we're done.
    exit 0
fi

echo "Moving cscope database to $DestDir"
for File in `ls cscope.*`; do
    NewFile=`echo $File | sed "s/cscope/cscope-$CscopeSubDirName/g"`
    mv $File $DestDir/$NewFile
    ln -s $DestDir/$NewFile $File
done 
echo "    Done"

exit 0


