#!/bin/bash

FunctionName=$1


Files=`grep -Ircl --include=*.{c,cpp,h} $FunctionName *`

for File in `grep -Ircl --include=*.{c,cpp,h} $FunctionName *`; do
    echo $File
done
