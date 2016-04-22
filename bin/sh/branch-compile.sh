#!/bin/sh

#global variables
CMD_PATH=/tools/swdev/bin
SRC_PATH=/project/swbuild1/$USER
SCRATCH_PATH=/scratch/17/$USER


if [ $# -ne 2 ]; then
    echo "usage: $SCRIPTNAME dir-name build-target"
    echo "    dir-name        : name of directory for src (e.g. sfi_158980)"
    echo "    build-target    : target for building src (all|SE1200|SE800|SE100)"
    exit 0
fi

BranchDir=$1
CompileTarget=$2

cd $SRC_PATH/$BranchDir/pkt
if [ "$?" -ne "0" ]; then
    echo  "%    ERROR: Could change to $SRC_PATH/$BranchDir/pkt..."
    exit 1
fi
echo  "Checking for valid scratch path $SCRATCH_PATH/$BranchDir..."
$CMD_PATH/scratch-config --check
if [ "$?" -ne "0" ]; then

    # scratch if directory did not exist
    if [ ! -d $SCRATCH_PATH/$BranchDir ]; then
        echo  "Scratch path $SCRATCH_PATH/$BranchDir does not exists, creating..."
        mkdir $SCRATCH_PATH/$BranchDir
        if [ ! -d $SCRATCH_PATH/$BranchDir ]; then 
            echo "%    ERROR: Could not create scratch dir @ $SCRATCH_PATH/$BranchDir. Abort"
            exit 1
        fi
        echo "    Done"
    fi

    #setup scratch directory
    cd $SRC_PATH/$BranchDir/pkt
    echo "Setting up scratch links for $BranchDir..."
    $CMD_PATH/scratch-config $SCRATCH_PATH/$BranchDir

    #$CMD_PATH/scratch-config fails, force cleanup
    if [ "$?" -ne "0" ]; then
        echo "%    ERROR: scratch setup failed, trying force-cleanup"
        $CMD_PATH/scratch-config --force-cleanup
        $CMD_PATH/scratch-config $SCRATCH_PATH/$BranchDir
    fi

    # currently clobber never fails so cannot be used to do clean setup
    #$CMD_PATH/scratch-config --, force cleanup
    #force cleanup fails, try clobber 
    #if [ "$?" -ne "0" ]; then
    #    echo "%    ERROR: scratch force cleanup failed, trying clobber"
    #    $CMD_PATH/scratch-config --clobber
    #fi
 
    #clobber fails, clear scratch directory
    if [ "$?" -ne "0" ]; then
        echo "%    ERROR: scratch force-cleanup failed, delete & recreate"
        rm -rf $SCRATCH_PATH/$BranchDir/*
        if [ "$?" -ne "0" ]; then
            echo "%    ERROR: Delete contents of $SCRATCH_PATH/$BranchDir failed...Abort"
            exit 1
        fi
        $CMD_PATH/scratch-config $SCRATCH_PATH/$BranchDir
    fi
fi
echo "    done"

#building tree for target
echo "Building tree $BranchDir for target $CompileTarget... "
cd $SRC_PATH/$BranchDir/pkt
if [ $2 = "all" ]; then 
    $CMD_PATH/emq --silent seos-all 
else
    $CMD_PATH/emq --silent seos PRODUCT=$CompileTarget
fi
echo "    done"

#check if builds are done
TODAY=`date '+%Y%m%d%n'`
echo "Today is $TODAY"
cd $SCRATCH_PATH/$BranchDir/images
for Ifile in `ls *.gz`; do
    fDate=`stat $Ifile --format='%x' | cut --bytes=1-4,6-7,9-10`    
    if [ $fDate -eq $TODAY ]; then
        echo "$Ifile compile successful"
    else
        echo "$Ifile - last compiled on `stat $Ifile --format='%x' | cut --bytes=1-10`"
    fi
done
echo "    done"
 
exit 0

