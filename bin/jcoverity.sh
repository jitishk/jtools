#!/bin/sh
RepoDir=$1
cd /project/swbuild9/ejitkol/$RepoDir/pkt/sw/se/xc/bsd/routing/rib
cov-private-build --web --branch=swfeature_int --modified-files="`git diff --name-only --relative HEAD~1 HEAD | xargs echo`" gmake PRODUCT=ASG-RP

