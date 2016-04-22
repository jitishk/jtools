#!/usr/bin/python

#TODO 
#1. Verify location of image
#2. Read topology from ARTS
#3. Store topology (?)


from subprocess import call
import sys
from topology import Topology
import os
import subprocess
import socket

#Globals for all simulators
user_name = os.environ.get("USER")
ssrsim_server = "ssrsim-poc-19.eld.sj.us.am.ericsson.se"
script_name = sys.argv[0]
ssrsim_root_path = "/ssrsim/" + user_name
ssh_port = 22

#ssrsim variables
topology_file = "topology"

def usage():
    print "%s [--name <toplogy name>] [--image <image location>] [--help]" % script_name
    print "%10s:\t%s" % ("--destroy", "destroy the topology")
    print "%10s:\t%s" % ("--image", "specify the location of sdk image")
    print "%10s:\t%s" % ("--help", "print this usage")
    print "%10s:\t%s" % ("--prepare", "prepare the image for ssr-sim")
    print "%10s:\t%s" % ("--create", "create the topology with associated chassis and bridges")
    print "%10s:\t%s" % ("--start", "start the topology")
    print "%10s:\t%s" % ("--access", "prints login information")
    print "%10s:\t%s" % ("--stop", "stop the topology")
    print "%10s:\t%s" % ("--topology", "name of the file with topology")
    print "%10s:\t%s" % ("--show-all", "Display all running chassis")


num_args = len(sys.argv)
if(num_args == 1):
    usage()
    sys.exit()

prepare = False
create = False
start = False
access = False
login = False
stop = False
destroy = False
show = False
clean = False

topology_file = ""
index = 1

for arg in sys.argv[1:num_args]: 
    if (arg == "--name"):
        topology_name = sys.argv[index+1]
    elif (arg == "--image"):
        image = sys.argv[index+1]
    elif (arg == "--help"):
        usage()
    elif (arg == "--prepare"):
        prepare = True
    elif (arg == "--create"):
        create = True
    elif (arg == "--start"):
        start = True
    elif (arg == "--access"):
        access = True
    elif (arg == "--stop"):
        stop = True
    elif (arg == "--login"):
        login = True
    elif (arg == "--topology"):
        topology_file = sys.argv[index+1]
    elif (arg == "--destroy"):
        destroy = True
    elif (arg == "--show-all"):
        if (os.path.exists('sdk/scripts/ssr-sim') == True):
            call(["sdk/scripts/ssr-sim", "show", "ALL"])
        else:
            print "sdk/scripts/ssr-sim not found"
        sys.exit()
    elif (arg == "--clean"):
        clean = True
    else:
        print "Unknown argument: %s, use --help to see all options" % arg 
    index = index + 1

if topology_file == '':
    print "Topology file not specified!"
    sys.exit()

if (os.path.exists(topology_file) == "False"):
    print "Topology file does not exists"
    sys.exit()

topology = Topology()
topology.set_topology(topology_file, ssrsim_root_path)
topology.display()

if (prepare == True):
    topology.prepare()

if (create == True):
    topology.create()

if (start == True):
    topology.start()

if (stop == True):
    topology.stop()

if (destroy == True):
    topology.destroy()

if (clean == True):
    topology.cleanup()

sys.exit()

