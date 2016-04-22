#!/bin/bash -x

#TODO:
#1. --latest with pick the latest version from sysbuild     - DONE
#2. --config will load config from file
#3. Reset configuration
#4. configure timeout idle/session to 99999
#5. getopts and usage                                       - in progress 
#6. Take array of IPs to load images                        - DONE
#7. Handle prompts for shell, CLI, and CLI Admin modes
#8. Interactive mode for logging into ref
#9. support partial tasks...only copy, or only attach etc.  - DONE
#10. Sanity check:
#   a. image exists
#11. Cleanup
#12. Colorify



RED="\033[0;31m"
NC="\033[0m" # No Color

usage () {
    ScriptName=$(basename "$0" .sh)
    echo "Load ipos-ref with latest image and install"
    echo "Usage: $ScriptName [-h|--help] <ref-ip> [ref-ip] ... [-i|--image <image>] [-s|--suffix <suffix>] [-c|--copy <file> [file] ... ]"
}

RefIP=$1
refip=true
refipcount=0

Copy=false
ItemCount=0
Items=()

User="root"
Password="ww"
ShellPrompt="~#"
CLIPrompt="[.*].*#"
Expect=`which expect`
DestFolder="/flash"
Image=

# for i in "$@"
while [[ $# > 0 ]]
do
   case $1 in
     -h|--help)
         usage
         exit 0
         ;;
     -i|--image)
         shift # past argument=value
         Image="${1}"
         refip=false
         Copy=false
         ;;
     -l|--latest-image)
         shift # past argument=value
         Image="/home/sysbuild/images/lsv/latest_linux_lsv_release"
         refip=false
         Copy=false
         ;;
     -s|--suffix)
         shift # past argument=value
         Suffix="${1}"
         refip=false
         Copy=false
         ;;
     -c|--copy)
         shift
         Copy=true
         refip=false
         ;;
     --default)
         DEFAULT=YES
         shift # past argument with no value
         ;;
     *)
         if [ $refip = true ]; then
             refipcount=$refipcount+1
             refips[$refipcount]=$1
         elif [ $Copy = true ]; then
             ItemCount=$ItemCount+1
             Items[$ItemCount]=$1
         fi
         shift
         ;;
    esac
done

# Add a user-specified suffix to differentiate between images
DestImage=
if [ ! -z $Suffix ]; then
    DestImage=$Suffix-$(basename $Image)
else
    DestImage=$(basename $Image)
fi

echo "Image         : $Image"
echo "Destination   : $User@$RefIP:/$DestFolder/$DestImage"
echo "Ref IPs       : ${refips[*]}"
echo "Copy Items    : ${Items[*]}"

for RefIP in ${refips[@]}; do
# Waiting for shell-prompt "~#" is not correct for scp. Works for now.

echo -e "\n${RED}Copying $Image to $RefIP:/$DestFolder/$DestImage ${NC}"
if [ $Image ]; then
$Expect <<EOD
    set timeout 120
    spawn scp $Image $User@$RefIP:/$DestFolder/$DestImage
    expect "password:"
    send "$Password\r"
    expect "$ShellPrompt"
EOD

echo -e "\n${RED}Loading $DestImage ${NC}"
$Expect <<EOD
    set timeout 120
    spawn ssh $User@$RefIP
    expect "password:"
    send "$Password\r"
    expect "$ShellPrompt"
    send "ipos_install.sh $DestFolder/$DestImage --start\r"
    expect "$ShellPrompt"
    send "exit\r"
EOD
fi

DestItem=
for Item in ${Items[@]}; do
# Copy items to ref
if [ ! -z $Suffix ]; then
    DestItem=$Suffix-$(basename $Item)
else
    DestItem=$(basename $Item)
fi
echo -e "\n${RED}Copying $Item to $RefIP:/$DestFolder/$DestItem ${NC}"
# Cannot indent this. Find a fix.
$Expect <<EOD
    set timeout 120
    spawn scp $Item $User@$RefIP:/$DestFolder/$DestItem
    expect "password:"
    send "$Password\r"
    expect "$ShellPrompt"
EOD
done # End for-loop of Items

done # End for-loop of RefIPs

