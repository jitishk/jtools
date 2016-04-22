#!/bin/bash


files=`find . -name "*.c"`
FileCount=0
LineCount=0
for file in $files; do
    gcc -C $file > temp
    echo "File: $file" 
    FileCount=$((FileCount + 1))
    if [ $FileCount -eq 5 ]; then
        exit 0
    fi
done

