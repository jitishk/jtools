#!/bin/bash -x
git clean -xdf --exclude="cscope*" --exclude="*.commit" --exclude="*.patch"
Repo=$(basename `pwd`)

if [ "$1" != "-i" ]; then
    if [ ! -d $ScratchDirectory/$Repo ];
    then
        echo "Scratch directory for repo $ScratchDirectory/$Repo not found";
        exit 0
    fi
    cd $ScratchDirectory/$Repo
    rm -rf pkt
    rm -rf tdm
    rm -rf plat
fi
rm -rf images
rm -rf obj
rm -rf README
rm -rf release*
rm -rf unstripped

