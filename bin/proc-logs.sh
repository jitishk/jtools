#!/bin/bash


if [ $1 = '-t' ]; then
	for file in `ls RIB_LOG*`; do
		logfile="${file%.*}".logs
		/usr/lib/siara/bin/ribd --logfile $file >> $logfile
	done
	exit 0
fi


for file in `ls RIB_LOG*`; do
	result=`/usr/lib/siara/bin/ribd --logfile $file | grep "$1"`
	if [ ! -z "$result" ]; then
		echo $file
	fi
done

