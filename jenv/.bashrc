#
# Basic environment variables
#

# don't overwrite exisiting files when redirecting output
set noclobber 
# set file creation mask so perms are 755
umask 022 
# keep history of last n commands
export HISTSIZE=100  

# save last n commands to a file
export SAVEHIST=100  

# notified immediately when background jobs are completed
set notify 

# coredump size is 0
ulimit -c 0 

export PATH=/tools/swdev/bin:$PATH
#
# OS dependant section. Place OS dependant settings here
#
HOSTTYPE=`uname -s`

case $HOSTTYPE in
 "NetBSD")
  export PATH=$HOME/shared/bin:/usr/local/bin:/bin:/sbin:/usr/sbin:/usr/pkg/bin:/usr/bin:/usr/X11R6/bin
 ;;
 "Linux")
  export PATH=$HOME/shared/bin:/usr/local/bin:/bin:/sbin:/usr/sbin:/usr/pkg:/usr/bin:/usr/X11R6/bin
 ;;
  "SunOS")
  export PATH=$HOME/shared/bin:/usr/local/bin:/usr/sbin:/usr/bin:/usr/openwin/bin:/usr/dt/bin
  export MOZILLA_HOME=/usr/local/netscape45
  export OPENWINHOME=/usr/openwin
  export MANPATH=/usr/share/man:/usr/man:/usr/local/man
;;
 *)
  ;;
esac

# Set up CVS
# Uncomment the lines below and set CVSROOT to your groups root cvs path.
#
#export CVS_RSH=ssh
#export CVSROOT=admin:/build/cvs


#
# Set default print queue
# Uncomment the line below and change the printer to the one you wish to print to.
#
#export PRINTER=p300-2-8k


#
# Setup modules
# Uncomment the line below and add the modules you wish to load
#

# set prompt
export PS1="\u@\h "

# We suggest you keep all of your aliases in a seperate file called .aliases
# If .aliases exists it will envoked by the next line:
if [ -f $HOME/.aliases ]; then
	 source $HOME/.aliases 
fi

