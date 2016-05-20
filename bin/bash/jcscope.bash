#!/usr/bin/bash
#TODO
# 01. Enable cscope indexing on files where we don't have write access
# 02. [DONE] Sanity check on directories
# 03. [DONE] Proper cleanup. Remove original files of softlinks.
# 04. [DONE] Handle invalid options
# 05. Handle sanity check for options when shifting.
# 06. Prevent deletion of cscope files in use.
# 07. error to string printing

E_INVALID_DIR_ERR=2
E_NO_OPT_ERR=1
E_SUCCESS=0

declare short_opt_a
declare long_opt_a
declare help_a
declare cb_a
declare jparams=$@

jopt_create () {
    Index=${#short_opt_a[*]}
    short_opt_a[$Index]=$1
    long_opt_a[$Index]=$2
    help_a[$Index]=$3
    cb_a[$Index]=$4
}

jopt_process () {
    # TODO: prevent searching through both long and short option arrays.
    # echo "jopt_process" $@

    for (( i=1; i<${#short_opt_a[*]}; i++)) {
        # echo "jopt_process" "$i" "${short_opt_a[$i]}" "${1}"
        if [[ "${short_opt_a[$i]}" = "${1}" ]]; then
            ${cb_a[$i]} $@
            return $E_SUCCESS
        fi
    }
    for (( i=1; i<${#long_opt_a[*]}; i++)) {
        # echo "jopt_process" "$i" "${long_opt_a[$i]}" "${1}"
        if [[ "${long_opt_a[$i]}" = "${1}" ]]; then
            ${cb_a[$i]} $@
            return $E_SUCCESS
        fi
    }
    return $E_NO_OPT_ERR
}

# jcscope
# Create cscope index @ source directory provided (. by default). The cscope
# files are moved to destination directory if provided (. by default).  Edit
# $filetypes to add/remove new file extensions that needs to be cscoped.

declare DestinationDirectory="."
declare SourceDirectory="."

usage () {
    echo "Usage: $ScriptName [-s|--src-dir <src_dir>] [-d|--dest-dir <dest_dir>] [-h|--help]"
    shift # Shift out the option parameter
    jparams=$@
    exit $E_SUCCESS  # Print usage and exit script.
}

set_dest_dir () {
    shift # Shift out the option parameter
    DestinationDirectory=$1
    if [[ ! -d $DestinationDirectory ]]; then
        echo "Invalid destination directory $DestinationDirectory"
        exit $E_INVALID_DIR_ERR
    fi
    echo "Cscope files will be moved to" $DestinationDirectory
    shift # Shift out the directory
    jparams=$@
}

set_src_dir () {
    shift # Shift out the option parameter
    SourceDirectory=$1
    if [[ -d $SourceDirectory ]]; then
        cd $SourceDirectory
    else
        echo "Invalid source directory $SourceDirectory"
        exit $E_INVALID_DIR_ERR
    fi
    echo "Cscope will be run @" $SourceDirectory
    shift # Shift out the directory
    jparams=$@
}

# Specify options for this script
jopt_create "-h" "--help"       "print script usage"                usage
jopt_create "-d" "--dest-dir"   "directory to store cscope files"   set_dest_dir
jopt_create "-s" "--src-dir"    "directory to cscope"               set_src_dir

# Process options passed as parameters to script
while [[ ! -z ${jparams[0]} ]]; do # When all options are quenched, the last one is zero length
    jopt_process $jparams
    rc=$?
    if [[ $rc -gt $E_SUCCESS ]]; then
        echo "Error $rc occurred. exiting..."
        exit $rc
    fi
done

# Sanity check parameters passed. Destination and source directory has been
# verified. PWD has been changed to source directory.

# Cleanup: Remove old cscope files
echo "Removing previous cscope files, if any..."
`ls -l cscope.* | grep -- '->' | sed -e's/.*-> //' | xargs rm`
rm cscope.*

filetypes=("[chsC]" "jam" "txt" "tidl" "cc" "py" "sh" "dot" "cmd" "java" "Jamfile" "tmpl")
touch cscope.files
for type in ${filetypes[@]}; do
    echo "collecting ".$type" files..."
    find . -name "*.$type" -print >> cscope.files
done

echo "building database..."
cscope -bq

# If not destination directory has been provided, our work is done.
if [[ $DestinationDirectory == "." ]]; then
    exit $E_SUCCESS
fi
 
# Move the cscope files to destination directory and provide symlinks.
if [[ $SourceDirectory = '.' ]]; then
    suffix="_${PWD##*/}" 
else
    suffix="_${SourceDirectory##*/}" 
fi
timestamp=$(date +"%e%b%y-%k:%M")
suffix=$suffix-"${timestamp}"

for File in `ls cscope.*`; do
    NewFile="$DestinationDirectory/`echo $File | sed "s/cscope/cscope$suffix/g"`"
    mv $File $NewFile
    ln -s $NewFile $File
done

exit $E_SUCCESS
