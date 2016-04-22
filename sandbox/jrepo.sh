#!/bin/bash
# TODO
# 1. getopts for bash (DONE)
# 2. checkout the branch instead of clone if the directory already exists, e.g.
#    14B should checkout rel_ssr:14b and 13_2 should rheckout rel_ssr:13_2 in same
#    directory.
#

Repository=
RepoCommand=
Branch=
DirSuffix=
Clean=false

usage () {
    ScriptName=$(basename "$0" .sh)
    echo "Usage: $ScriptName [-h|--help] -b <lsv|14b|int|cmcc|14_2|12_2_reboot> [-d <repo-dir>] [-c|--clean]"
    echo "       -h|--help     : Print usage"
    echo "       -c|--clean    : clean prexisting directories"
    echo "       -b|--branch   : specify working branch to checkout"
    echo "       -d|--repo-dir : specify directory suffix for repository"
    echo "Example: $ScriptName -r lsv -d evs --clean"
    echo "         Clean prexisting directory:ipos-evs, authclone repository:ipos branch:lsv to directory:ipos-ev"

}

TEMP=`getopt -o hcb:d: --long help,clean,repo:repo-dir -n "$ScriptName".sh -- "$@"`
eval set -- "$TEMP"

while true; do
    case "$1" in
        -h|--help)  usage; exit 0; shift ;;
        -c|--clean) Clean=true; shift ;;
        -b|--branch)  Branch=$2; shift 2 ;;
        -d|--repo-dir) DirSuffix=$2; shift 2 ;;
        --) shift; break ;;
        *) echo "Invalid Option specified: $1" ; exit 1 ;;
    esac
done

# For a give parameter, translate to repo and the appropriate git checkout
# command. 
# e.g. To checkout LSV, the parameter "lsv" is translated as repository:ipos
# and branch:lsv, i.e. as per git checkout command "ipos -b lsv"
get_repo_for_branch () {
    case "$1" in
        "lsv")
            RepoCommand="ipos -b lsv"
            Repository="ipos"
            ;;
        "14b")
            RepoCommand="rel_ssr -b REL_IPOS_14_1_127"
            Repository="rel_ssr"
            ;;
        "12_2_reboot")
            RepoCommand="rel_ssr -b reboot_1221121332"
            Repository="rel_ssr"
            ;;
        "int")
            RepoCommand="ssr -b integration"
            Repository="ssr"
            ;;
        "cmcc")
            RepoCommand="proto -b REL_IPOS_15_2_129_CMCC_BMT"
            Repository="proto"
            ;;
        "14_2")
            RepoCommand="ipos -b REL_IPOS_14_2"
            Repository="ipos"
            ;;
         *)
            echo "Error: Invalid repository/branch: $name"
            ;;
    esac
}

# Sanity checks
if [ -z $Branch ];
then
    echo "Error: No branch specified"
    exit 1
fi

get_repo_for_branch $Branch
if [ -z $Repository ];
then 
    echo "Error: No repository found for $Branch"
    exit 1
fi

# Set checkout directory with custom ".repo" extension
if [ ! -z $DirSuffix ];
then
    RepoDirectory="$Repository-$DirSuffix.repo"
else
    RepoDirectory="$Repository.repo"
fi

# Set workspace directory
if [ -d "$WorkspaceDirectory/$RepoDirectory" ];
then
    if [ $Clean = true ];
    then
        echo "Removing $WorkspaceDirectory/$RepoDirectory"
        rm -rf "$WorkspaceDirectory/$RepoDirectory"
    else
        echo "Repo $WorkspaceDirectory/$RepoDirectory exists"
        exit 0
    fi
fi

# Set scratch directory
if [ -d "$ScratchDirectory/$RepoDirectory" ];
then
    if [ $Clean = true ];
    then
        echo "Removing $ScratchDirectory/$RepoDirectory"
        rm -rf "$ScratchDirectory/$RepoDirectory"
    else
        echo "Repo $ScratchDirectory/$RepoDirectory exists"
        exit 0
    fi
fi

# Authclone ipos lsv 
cd $WorkspaceDirectory
echo "Cloning $Repository repository to $WorkspaceDirectory/$RepoDirectory"
authclone $RepoCommand -d "$RepoDirectory"

# Configure build paths in scratch
cd $RepoDirectory
scratch-config "$ScratchDirectory/$RepoDirectory"

# Update cscope
jcscope "$WorkspaceDirectory/$RepoDirectory" "$ScratchDirectory/$RepoDirectory"
