#!/bin/bash
# slight modification of emtfere's setup-ssrsim-copy script

function get_file_date() {
    local return_date=$(date --utc --reference="$1" +%s 2>/dev/null)
    if [ "$return_date" == "" ]; then
        return_date=0
    fi  
    echo "$return_date"
}

# Copy the newest file if it was built after the last checkout
function copy_newly_built() {
    local FILE=$1
    local DATE_CO=$2
    local PATH1=$3
    local PATH2=$4
    local TO_PATH=$5

    if [ -f "$PATH1/$FILE" ]; then
        local DATE1=$(get_file_date $PATH1/$FILE)
    fi  
    if [ -f "$PATH2/$FILE" ]; then
        local DATE2=$(get_file_date $PATH2/$FILE)
    fi  
    if [ "$DATE1" == "" ] && [ "$DATE2" == "" ]; then
        echo "$FILE not built."
        return 1
    fi  
    if [ "$DATE2" == "" ] ||
       ( [ "$DATE1" != "" ] && [ $DATE1 -gt $DATE2 ] ); then
        if [ $DATE1 -gt $DATE_CO ]; then
            echo "copy $PATH1/$FILE"
            scp $PATH1/$FILE $RP_NAME:$TO_PATH
            return $?
        fi
    else
         if [ $DATE2 -gt $DATE_CO ]; then
             echo "copy $PATH2/$FILE"
             scp $PATH2/$FILE $RP_NAME:$TO_PATH
             return $?
         fi
    fi  
    echo "$FILE older than last checkout, not copying."
    return 1
}

# only copy if newer than checkout
# args: filename, proc name (optional), checkout date
function whitelist_binary() {
    local DATE_CO=${@:$#} # last argument
    local PATH_DYN="$WORKSPACE/pkt/xc-linux-x86-64/linux/Bin"
    local PATH_ST="$WORKSPACE/pkt/xc-linux-x86-64-static/linux/Bin"
    copy_newly_built $1 $DATE_CO $PATH_DYN $PATH_ST "/root"
    if [ $? -eq 0 ] && [ $# -eq 3 ]; then
        echo $2 >> $F_PROC_REST
    fi  
}
function whitelist_library() {
    local DATE_CO=${@:$#} # last argument
    local PATH_DYN="$WORKSPACE/pkt/xc-linux-x86-64/linux/Lib"
    local PATH_ST="$WORKSPACE/pkt/xc-linux-x86-64-static/linux/Lib"
    copy_newly_built $1 $DATE_CO $PATH_DYN $PATH_ST "/usr/lib/siara/lib64"
}

RP_NAME=$1
WORKSPACE=$2
TYPE=$3
FILE_NAME=$4
PROC_NAME=$5

F_PROC_REST="$PWD/.ssrsim-proc-rest"

cd $WORKSPACE/
DATE_LAST_CHECKOUT=$(date -d "$(git reflog --date=local | grep checkout | head -1 | sed 's|.*@{\([^}]*\).*|\1|g')" '+%s')

case "$TYPE" in
    'bin')
	if [ "$PROC_NAME" ]; then
            whitelist_binary $FILE_NAME $PROC_NAME $DATE_LAST_CHECKOUT
	else
            whitelist_binary $FILE_NAME $DATE_LAST_CHECKOUT
	fi
        ;;
    'lib')
        whitelist_library $FILE_NAME $DATE_LAST_CHECKOUT
        ;;
esac
