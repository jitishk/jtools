#!/usr/bin/python

from subprocess import call
import os
import sys

import fileinput
import pickle

ssr_sim_script = "sdk/scripts/ssr-sim"

class Wireup:
    def __init__(self, card_name, port):
        self.card_name = card_name
        self.port = port
    def display(self):
        print "\t%s:%d" % (self.card_name, self.port)

class Bridge:
    'Class for Bridge'

    def __init__(self, name):
        self.name = name
        self.wireups = []

    def display(self):
        print "Bridge: %s" % self.name
        for wireup in self.wireups:
            wireup.display()

    def add_wireup(self, card_name, port):
        self.wireups.append(Wireup(card_name, port))

    def create(self):
        call([ssr_sim_script, "create", "bridge", self.name]) 
        self.wireup()

    def wireup(self):
        for wireup in self.wireups:
           port_name = "port:" + str(wireup.port)
           call([ssr_sim_script, "wireup", self.name, wireup.card_name, port_name]) 

    def wiredown(self):
        for wireup in self.wireups:
           port_name = "port:" + str(wireup.port)
           call([ssr_sim_script, "wiredown", self.name, wireup.card_name, port_name]) 

    def destroy(self):
        self.wiredown()        
        call([ssr_sim_script, "delete", self.name]) 

###############################################################################
# Class Chassis
###############################################################################

class Chassis:
    'Class for Chassis'

    def __init__(self, name, num_rps, num_lcs):
        self.name = name
        self.rps = []
        for num in range(0, num_rps):
            self.rps.append("rp" + str(num+1) + "-" + name)
        self.lcs = []
        for num in range(0, num_lcs):
            self.lcs.append("lc" + str(num+1) + "-" + name)
        self.num_rps = num_rps
        self.num_lcs = num_lcs

    def display(self):
        print "Chassis: %s" % self.name
        print "\tNum RPs: %d" % self.num_rps
        print "\tNum LCs: %d" % self.num_lcs
        print "\tRPs: ", self.rps
        print "\tLCs: ", self.lcs

    def create(self):
        print "Creating Chassis: %s" % self.name
        call([ssr_sim_script, "create", "chassis", self.name]) 
        index = 1
        for rp in self.rps:
            print "Creating RP: %s" % rp
            call([ssr_sim_script, "create", "rpsw", rp]) 
            print "Inserting %s in %s @ RPSW%d" % (rp, self.name, index)
            call([ssr_sim_script, "insert", rp, self.name, "RPSW" + str(index)]) 
            index += 1

        index = 1
        for lc in self.lcs:
            print "Creating LC: %s" % lc
            call([ssr_sim_script, "create", "10ge-10-port", lc]) 
            print "Inserting %s in %s @ %d" % (lc, self.name, index)
            call([ssr_sim_script, "insert", lc, self.name, str(index)]) 
            index += 1

    def start(self):
        call([ssr_sim_script, "start", self.name]) 

    def stop(self):
        call([ssr_sim_script, "stop", self.name])

    def destroy(self):
        index = 1
        for rp in self.rps:
            print "Removing %s from %s @ RPSW%d" % (rp, self.name, index)
            call([ssr_sim_script, "remove", rp, self.name]) 
            print "Deleting RP: %s" % rp
            call([ssr_sim_script, "delete", rp]) 
            index += 1

        index = 1
        for lc in self.lcs:
            print "Removing %s from %s @ %d" % (rp, self.name, index)
            call([ssr_sim_script, "remove", lc, self.name]) 
            print "Creating LC: %s" % lc
            call([ssr_sim_script, "delete", lc]) 
            index += 1
 
        print "Deleting Chassis: %s" % self.name
        call([ssr_sim_script, "delete", self.name]) 

    def login(self, rp):
        call(["sdk/scripts/ssr-sim-console", self.rps[rp-1]]) 

    def get_lc_name(self, lc_index):
        return self.lcs[lc_index]

###############################################################################
# Class Topology
###############################################################################
 
class State:
    NONE = 'NONE'
    INIT = 'INIT'
    PREPARED = 'PREPARED'
    CREATED = 'CREATED'
    STARTED = 'STARTED'
    STOPPED = 'STOPPED'
    DESTROYED = 'DESTROYED'
    CLEANED = 'CLEANED'
 
class Topology:
    '''Class for Topology'''

    name = ''
    image = ''
    chasses = []
    bridges = []
    state = State.NONE
    toplogy_file = ''

    ##################### Initializing functinos #####################
    def __init__(self):
        print "Creating Topology"

    def set_topology(self, topology_file, ssrsim_root_path):
        self.topology_file = topology_file
        (self.name, self.image, num_chassis, num_rps, num_lcs, connections, self.state) = \
                self.read_topology(topology_file)

        print "Reading Topology"
        if self.name == '':
            print "Topology Name cannot be empty" 
            sys.exit()
        if self.image == '':
            print "Topology Image cannot be empty" 
            sys.exit()
        '''
        '''
        self.sdk_path = ssrsim_root_path + "/" + self.name + "/sdk"
        for i in range(num_chassis):
            self.add_chassis(num_rps, num_lcs)
        for i in range(len(connections)):
            self.add_bridge()
            (chs, lcs, ports) = self.parse_connection(connections[i])
            for j in range(len(chs)):
                self.add_bridge_wireup(i, chs[j], lcs[j], ports[j])

        '''Update state to indicate initialization'''
        if (self.state == State.NONE):
            self.update_state(State.INIT)

    def parse_connection(self, connection):
        wireups = connection.split('-')
        chs = []
        lcs = []
        ports = []
        for wire in wireups:
            c_l_p = wire.strip().split('/')
            chs.append(int(c_l_p[0].strip()))
            lcs.append(int(c_l_p[1].strip()))
            ports.append(int(c_l_p[2].strip()))
        return (chs, lcs, ports)
 
    def add_chassis(self, num_rps, num_lcs):
        '''
            Add a new chassis to toplogy.
        '''
        index = len(self.chasses) + 1
        name = self.name + "-ch" + str(index)
        self.chasses.append(Chassis(name, num_rps, num_lcs))

    def add_bridge(self):
        '''
            Add a new bridge to toplogy. A name is automatically
            selected based on the topology name.
        '''
        index = len(self.bridges) + 1
        name = self.name + "-br" + str(index)
        self.bridges.append(Bridge(name))

    def add_bridge_wireup(self, bridge_index, chassis_index, card_index, port):
        '''
            Configure the wireup of a bridge. Provide the chassis
            index and card index and port to be connected to bridge.
        '''
        bridge = self.bridges[bridge_index]
        card_name = self.chasses[chassis_index-1].get_lc_name(card_index-1)
        bridge.add_wireup(card_name, port) 


    ##################### Prepare functions #####################
    def prepare(self):
        if (os.path.exists(self.image) == False):
            print "Image not found at %s" % self.image
            sys.exit()

        if (os.path.exists(self.sdk_path) == True):
            print "Previous image already exists. Skipping extraction and prepare"
            return

        print "Preparing topology with image %s" % self.image
        call(["tar", "-xzf", self.image ])
        if (os.path.exists(ssr_sim_script) == False):
            print "Could not find ssrsim script %s" % ssr_sim_script
            sys.exit()

        call([ssr_sim_script, "prepare"])
        self.update_state(State.PREPARED)
        return True

    ##################### Create functions #####################
    def create(self):
        if (self.state != State.PREPARED):
            self.prepare()

        print "Creating Topology..."
        for chassis in self.chasses:
            chassis.create()
        for bridge in self.bridges:
            bridge.create()
        self.update_state(State.CREATED)

    def create_chassis(self, index):
        self.chasses[index].create()

    ##################### Start functions #####################
    def start(self):
        if (self.state != State.CREATED):
            self.create()

        print "Starting Topology..."
        for chassis in self.chasses:
            chassis.start()

        self.update_state(State.STARTED)

    def start_chassis(self, index):
        self.chasses[index].start()

    ##################### Stop functions #####################
    def stop(self):
        if self.state != State.STARTED:
            print "Topology not started, cannot stop. State: %s" % (self.state)
            return
        if self.state == State.STOPPED:
            print "Topology already stopped."
            return

        print "Stopping Topology..."
        for chassis in self.chasses:
            chassis.stop()
        self.update_state(State.STOPPED)

    def stop_chassis(self, index):
        self.chasses[index].stop()

    ##################### Destroy functions #####################
    def destroy(self):
        if self.state == State.STARTED:
            self.stop()

        if self.state == State.DESTROYED:
            print "Topology already destroyed."
            return

        print "Destroying Topology..."
        if self.state != State.STOPPED:
            print "Topology not stopped, cannot destroy. State: %s" % (self.state)
            return

        for bridge in self.bridges:
            bridge.destroy()

        for chassis in self.chasses:
            chassis.destroy()

        self.update_state(State.DESTROYED)

    def destroy_chassis(self, index):
        self.chasses[index].destroy() 

    ##################### Cleanup functions #####################
    def cleanup(self):
        ''' 
            Cleanup a Topology:
            Calls the sdk script for cleanup. If toplogy is already created, 
            it is destroyed first.
        '''
        if self.state == State.STARTED:
            self.stop()
        if self.state == State.STOPPED:
            self.destroy()
        if self.state == State.CLEANED:
            print "Topology already cleaned."
            return
        if self.state != State.DESTROYED:
            print "Topology not destroyed, cannot clean. State: %s" % (self.state)
            return

        call([ssr_sim_script, "clean"]) 

        self.update_state(State.NONE)

    #####################  IO functions #####################
    def login(self):
        for chassis in self.chasses:
            print "./sdk/scripts/ssr-sim-console ", chassis.rps[0]

    def update_state(self, state):
        self.state = state
        state_line = "state = %s" % self.state

        new_lines = []
        fp = open(self.topology_file, 'r')
        for line in fp:
            if (line.find("state") >= 0):
                new_lines.append(state_line)
            else:
                new_lines.append(line)
        fp.close()

        fp = open(self.topology_file, 'w')
        for line in new_lines:
            fp.write(line)
        fp.close()

    def read_topology(self, topology_file):
        connections = [];
        num_chassis = 1;
        num_rps = 1
        num_lcs = 0
        fp = open(topology_file, 'rw')
        for line in fp:
            line = line.strip(' \n')
            if (line[0] == '!'):
                continue
            params = line.split('=')
            if params[0].strip() == 'name':
                name = params[1].strip()
            elif params[0].strip() == 'image':
                image = params[1].strip()
            elif params[0].strip() == 'num_chassis':
                num_chassis = int(params[1].strip())
            elif params[0].strip() == 'num_rps':
                num_rps = int(params[1].strip())
            elif params[0].strip() == 'num_lcs':
                num_lcs = int(params[1].strip())
            elif params[0].strip() == 'connection':
                connections.append(params[1].strip())
            elif params[0].strip() == 'state':
                state = params[1].strip()
            else:
                print "Unknown line in Toplogy file: %s" % line
        fp.close()

        return (name, image, num_chassis, num_rps, num_lcs, connections, state)
 
    def display(self):
        print "Name: %s" % self.name
        print "Image: %s" % self.image
        print "Chassis: %d" % len(self.chasses)
        for chassis in self.chasses:
            chassis.display()
        for bridge in self.bridges:
            bridge.display()
        print "State: %s" % self.state
 
