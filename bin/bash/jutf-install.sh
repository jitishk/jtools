#!/bin/bash -x
# TODOs:
# 1. getopts
# 2. Store state of installations. Enable recovery from multiple overlapping
#    installs
# 3. Make functions
# 4. Sanity check for files

# Change working directory to root
cd /

if [ "$2" = "-r" ]; then
    echo "Reverting to base utf"
    UtfBaseTarBall=$1
    # extract the file list of loaded utf-tarball
    tar -xf $UtfBaseTarBall utf-new.files

    FileCount=0
    for File in `cat utf-new.files`; do
        # Ignore directories
        if [ -d $File ]; then
            continue
        fi
        # If a file exists, delete it. 
        if [ -f $File ]; then
            rm -rf $File
        fi
        FileCount=$((FileCount + 1))
    done

    # Restore files from utf base tarball
    tar -xzf $UtfBaseTarBall
else
    UtfTarBall=$1
    UtfBaseTarBall="utf-base.tar"
    # Store a list of all files that will be extracted
    tar -tf $UtfTarBall > utf-new.files

    FileCount=0
    for File in `cat utf-new.files`; do
        #FileName=${File##*/}
        # Ignore directories
        if [ -d $File ]; then
            continue
        fi

        # If a file exists, archive it as these will be overwritten.
        if [ -f $File ]; then
            tar --remove-files -uf $UtfBaseTarBall $File
        fi
        FileCount=$((FileCount + 1))
    done

    # Store the list of new utf files
    tar --remove-files -uf $UtfBaseTarBall utf-new.files

    # Compress the tarball
    gzip $UtfBaseTarBall

    # Uncompress the new utf files
    tar -xvzf $UtfTarBall
fi
