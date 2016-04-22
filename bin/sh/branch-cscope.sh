#!/bin/sh

#global variables
CMD_PATH=/tools/swdev/bin
SRC_PATH=/project/swbuild9/$USER
SCRATCH_PATH=/scratch/9/$USER
MYPWD=`pwd`

if [ $# -ne 2 ]; then
    echo "usage: $SCRIPTNAME branch-dir root-dir-name"
    echo "  branch-dir      : name of directory for src (e.g. sfi_158980)"
    echo "  root-dir-name   : root directory for cscope (root|rib|pwd)"
    exit 2
fi

BranchDir=$1
RootDir=$2

# Sanity check directories
echo "Sanity check for directories... " 
if [ ! -d $SRC_PATH/$BranchDir ]; then
    echo "    %ERROR: Directory $BranchDir does not exist"
    exit 1
fi

case $RootDir in
    root)
        CscopeRootDir=.
        ;;
    pwd)
        CscopeRootDir=`echo $MYPWD | sed "s/\/project\/swbuild9\/ejitkol\/$BranchDir\///g"`
        ;;
    pkt)
        CscopeRootDir=pkt
        ;;
    tdm)
        CscopeRootDir=tdm
        ;;
    rib)    
        CscopeRootDir=pkt/sw/se/xc/bsd/routing/rib
        ;;
    rtd)    
        CscopeRootDir=pkt/sw/se/xc/bsd/routing/rib/unit-test/rib_unit_test/rib_testd
        ;;
    *)
        echo "Cannot determine root directory"
        break
esac
cd $SRC_PATH
cd $BranchDir
if [ ! -d $CscopeRootDir ]; then
    echo "    %ERROR: Directory $SRC_PATH/$CscopeRootDir does not exist"
    exit 1
fi

cd $SCRATCH_PATH
if [ ! -d $BranchDir ]; then
    echo "    %ERROR: Directory $SCRATCH_PATH/$BranchDir does not exist... creating"
    mkdir $BranchDir
    if [ ! -d $BranchDir ]; then
        echo "    %ERROR: Directory $SCRATCH_PATH/$BranchDir create failed... aborting"
        exit 1
    fi
fi
echo "    Done"

echo "Removing prexisting cscope files..."
rm -rf $SRC_PATH/$BranchDir/$CscopeRootDir/cscope.*
rm -rf $SCRATCH_PATH/$BranchDir/cscope_${CscopeRootDir}.*
echo "    Done"

# Creating cscope database
cd $SRC_PATH/$BranchDir/$CscopeRootDir
echo "collecting *.[chs] files..."
find . -name "*.[chs]" -print > cscope.files
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

echo "collecting make files..."
find . -name "Makefile" -print >> cscope.files
echo "    Done"
 
echo "collecting .java files..."
find . -name "*.java" -print >> cscope.files
echo "    Done"
 
echo "building database..."
cscope -bq
echo "    Done"

# Moving cscope database scratch
echo "Moving cscope files to $SCRATCH_PATH/$BranchDir and linking... "
echo $CscopeRootDir
for File in `ls cscope.*`; do
    Newfile=`echo $File | sed "s/cscope/cscope_$RootDir/g"`
    mv $File $SCRATCH_PATH/$BranchDir/$Newfile
    ln -s $SCRATCH_PATH/$BranchDir/$Newfile $File
done 
echo "    Done"
exit 0
