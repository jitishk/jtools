#!/usr/bin/python

import sys
import pexpect

def onpath_connect(onpath_ip, onpath_port, port1, port2):
    prompt = '=>'
    print 'Onpath Login into ' + onpath_ip  + ' port ' + onpath_port
    onpath = pexpect.spawn ('telnet ' + onpath_ip +  ' ' + onpath_port)
    onpath.logfile_read = open('results.txt', 'w')
    onpath.expect(prompt)
    print onpath.before

    onpath.sendline ('logon ecpuser')
    onpath.sendcontrol('m')
    onpath.expect ('Password:')
    print onpath.before
    onpath.sendline ('ecpuser1')
    onpath.sendcontrol('m')
    onpath.expect(prompt)
    print onpath.before

    onpath.sendline ('conn port ' + port1 + ' to ' + port2 + ' force')
    onpath.sendcontrol('m')
    onpath.expect(prompt)
    print onpath.before
    print 'Done'
    return onpath

onpath_ip = '10.126.191.53'
onpath_port = '53058'

num_args = len(sys.argv)
if(num_args <> 3):
    print 'Usage: ' + sys.argv[0] + ' port1 port2' 
    sys.exit()

onpath_connect('10.126.191.53', '53058', sys.argv[1], sys.argv[2])
