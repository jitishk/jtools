#!/usr/bin/sh

ErrIncorrectArgCount=-1
ErrDirNotFound=-2
ErrDirCreate=-2
ErrGitBranchCheckout=-3
ErrGitMasterCheckout=-4
ErrGitBranchRebase=-5
ErrGitPullOrigin=-6


User=$USER
ProjectDir=/project/swbuild9/$User
ScratchDir=/scratch/9/$User

ExpectedArgCount=2


if [ $# -lt $ExpectedArgCount ]; then
    echo "Usage: $0 <repository-directory> [clean|clobber|compile|update]"
    exit $ErrIncorrectArgCount
fi

RepositoryDir=$1
Scope=$2
Script=`echo $0 | sed 's/\.\///g' | sed 's/\.sh//g'` 
Script=${0##*/}

TempDir=`mktemp -d -t $Script.XXXXXXXXXX`
Clean=false
Clobber=false
Compile=false
GitUpdate=false

#Script argument storage and verification
if [ ! -d $ProjectDir ]; then
    echo "ERROR: $ProjectDir not found" 1>&2
    exit $ErrDirNotFound
fi

if [ ! -d $ScratchDir ]; then
    echo "ERROR: $ScratchDir not found" 1>&2
    exit $ErrDirNotFound
fi

if [ ! -d $ProjectDir/$RepositoryDir ]; then
    echo "ERROR: $ProjectDir/$RepositoryDir not found" 1>&2
    exit $ErrDirNotFound
fi
if [ ! -d $ProjectDir/$RepositoryDir/pkt ]; then
    echo "ERROR: Invalid repo? $ProjectDir/$RepositoryDir/pkt not found" 1>&2
    exit $ErrDirNotFound
fi

for arg in "$@"
do
    if [ $arg == 'clean' ]; then
        Clean=true
    elif [ $arg == 'clobber' ]; then
        Clobber=true
    elif [ $arg == 'compile' ]; then
        Compile=true
    elif [ $arg == 'update' ]; then
        GitUpdate=true
    fi
done

if $Clobber; then
    echo "Change to $ProjectDir/$RepositoryDir"
    cd $ProjectDir/$RepositoryDir/pkt
    scratch-config --clobber;
fi

if $Clean; then
    echo "Change to $ProjectDir/$RepositoryDir"
    cd $ProjectDir/$RepositoryDir
    echo "Running git clean"
    git clean -xdf -e 'cscope*' -e '*.patch' 2> $TempDir/git-clean.err | tee $TempDir/git-clean.logs
fi

#Compile parameters
Debug='DBG=yes'
ScratchFlags=''
if $Compile; then
    echo "Compile: Changing to $ProjectDir/$RepositoryDir"
    cd $ProjectDir/$RepositoryDir/pkt

    #Check scratch directory setup
    scratch-config --check 2> $TempDir/scratch-config.err 1> $TempDir/scratch-config.log
    test $(grep "You do not have \/scratch symlinks in your work directory" $TempDir/scratch-config.err -c) > 0; ScratchSymLinksNotSetup=true

    #If scratch directory exists, force reuse it, and configure links
    if [ -d $ScratchDir/$RepositoryDir ] && [ $ScratchSymLinksNotSetup ] ; then
        echo "Scratch directory not empty. Force reusing"
        ScratchFlags='--force-reuse'
    fi

    scratch-config $ScratchFlags $ScratchDir/$RepositoryDir 2>> $TempDir/scratch-config.err 1>> $TempDir/scratch-config.log 
    if [ "$?" -ne "0" ]; then
        echo "ERROR: Scratch directory not configured"
        exit
    fi

    echo "Compiling..."
    emq -s PRODUCT=ASG $Debug 2> $TempDir/emq.err 1> $TempDir/emq.logs
    #scratch-config --cteck | tee temp | grep "scratch-config"
fi

if $GitUpdate; then
    echo "Change to $ProjectDir/$RepositoryDir"
    cd $ProjectDir/$RepositoryDir
    test $(git checkout master) != "0"; exit $ErrGitMasterCheckout
    test $(git pull origin) != "0"; exit $ErrGitPullOrigin
    test $(git checkout $Branch) != "0"; exit $ErrGitBranchCheckout
    test $(git rebase master) != "0"; exit $ErrGitBranchRebase
fi

echo "DONE $TempDir"
exit


echo $PWD
$CurrentBranch=`git branch`

#| grep '^\*'`
#| sed 's/^/* //g'`
echo $CurrentBranch
exit

scratch-config --check
if [ "$?" -ne "0" ]; then

else

fi
 
# If scratch does not exist create it.
if [ ! -d $ScratchDir/$RepositoryDir ]; then
    echo  "Scratch path $ScratchDir/$RepositoryDir does not exists, creating..."
    mkdir $ScratchDir/$RepositoryDir
    if [ ! -d $ScratchDir/$RepositoryDir ]; then 
        echo "ERROR: Could not create scratch dir @ $ScratchDir/$RepositoryDir. Abort"
        exit $ErrDirCreate
    fi
    echo "    Done"
fi
 

TempDir=`mktemp -d $0`
git diff --name-only > $TempDir/diff-files
git add `cat $TempDir/diff-files`
git commit -m '$0 Stashing changes'

git checkout master
git pull origin

if [ $Rebase == 1 ]; then
    git checkout $CurrentBranch
    git rebase master
fi









echo $RepositoryDir
echo $Scope






