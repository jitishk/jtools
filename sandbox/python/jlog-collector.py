#!/usr/bin/python
import os
import sys
import getpass
from subprocess import call
from chassislib import chassis_login

import pexpect

import getopt


#Get commands
basic_commands_per_context  = [ 
                                "show clock",
                                "show ip route all",
                                "show ip route next-hop detail",
                                "show ip route registered next-hop",
                                "show ip route registered prefix",
                                "show ip route client",
                                "show ip route fib-client",
                            ]

global_commands             = [ 
                                'show clock',
                                'show system status detail',
                                'show system status detail card all',
                                'show process rib thread-info',
                                'show process rib thread-history',
                                'show process rib chunk-statistics',
                                'show process rib shared-memory-statistics',
                                'show ipc process rib detail',
                                'show ip route counters global',
                                'show ip route xcrp',
                                'show clock',
                            ]

rib_log_commands            = [ 
                                'terminal length 0',
                                'show clock',
                                'show ip route log',
                                'show ip route log message detail',
                                'show ip route log config detail',
                                'show ip route log route detail',
                                'show ip route log protocol 80 detail',
                                'show ip route log protocol 16 detail',
                                'show ip route log protocol 8 detail',
                                'show clock',
                            ]
 
clients_log = {'bgp':80, 'static':16, 'tunnel':8}


hostname = ''
ip_address = ''
file_suffix = ''

'''
try:
   opts, args = getopt.getopt(sys.argv[1:],'h:i:f:',['hostname=','ip-address=', 'file-suffix='])
except getopt.GetoptError:
    print 'test.py -h <hostname> -i <IP> -f <file_suffix>'
    sys.exit(2)
for opt, arg in opts:
    if opt in ('-h', '--hostname'):
        hostname = arg    
    elif opt in ('-i', '--ip-address'):
         ip_address = arg
    elif opt in ("-f", "--file-suffix"):
        file_suffix = arg
if hostname =='' and ip_adress=='':
    print 'Please provide hostname or IP address of chassis'
    sys.exit()
'''


    
def chassis_load_image(chassis, image):
    print "Loading chassis with %s" % (image)
    release_download = "release download ftp://ejitkol@10.10.10.22/" + image
    chassis.sendline(release_download)
    password = getpass.getpass()
    chassis.expect('password:')
    chassis.sendline(password)
    chassis.expect('Are you sure you wish to erase this release')
    chassis.sendline('y')
    chassis.expect('\[local\]', timeout=900)
    print 'Done'

def execute_commands(chassis, context_name, commands, file_name = None):
    context_prompt = '[' + context_name + ']'

    # Change context and start file
    command = 'context ' + context_name
    echo_command = 'echo "' + context_prompt + command + '"'
    chassis.sendline(echo_command + ' | save ' + file_name)
    chassis.sendline(command + ' | save ' + file_name)

    # Set terminal length to 0
    chassis.sendline('terminal length 0')
    chassis.expect('\[local\]', 60)

    # Execute each command in context
    for command in commands:
        echo_command = 'echo "' + context_prompt + command + '"'
        print 'Command: ' + command
        chassis.sendline(echo_command + " | append " + file_name + ' | grep kkkk')
        chassis.sendline(command + " | append " + file_name + ' | grep kkkk')
        chassis.expect('\[local\]', 60)

    chassis.sendline("context local")
    chassis.expect('\[local\]')

def config_logs(chassis, clients, slots):
    print 'Configuring RIB logs'
    chassis.sendline('config')
    chassis.sendline('context local')
    chassis.sendline('ip log route size 65535')
    chassis.sendline('ip log message size 65535')
    for client in clients:
        chassis.sendline('ip log protocol ' + str(clients_log[client]) +
                ' size 66535')
    for slot in slots:
        chassis.sendline('ip log slot ' + slot + ' ingress size 65535')
        chassis.sendline('ip log slot ' + slot + ' egress size 65535')
    chassis.sendline('commit')
    chassis.sendline('end')
    chassis.expect('\[local\]')

num_args = len(sys.argv)
if(num_args < 2):
    print 'Usage: ' + sys.argv[0] + ' hostname file_suffix'
    sys.exit()
hostname = sys.argv[1]
if (num_args == 3):
    file_suffix = sys.argv[2]

debug_dir = '/md/riblogs/'
local_context = 'local'
global_file = debug_dir + 'rib_global_' + file_suffix + '.show'
rib_logs_file = debug_dir + 'rib_logs_'+ file_suffix + '.show'
username = 'test'
password = 'test'
#hostname = 'sjl3-ecp-ssr' + hostname + '.eld'
image = "/archive/build-images/REL_IPOS_13_1_114/SEOS-ASG-pkg-SSR-13.1.114.0.265.tar.gz"


chassis = chassis_login(hostname, username, password)

# chassis_load_image(chassis, image)
# config_logs(chassis, ['tunnel', 'static'],[])

chassis.sendline('mkdir ' + debug_dir)
chassis.expect('\[local\]')

#Execute global commands in local context
execute_commands(chassis, 'local', global_commands, global_file)

#Execute show log commands in local context
#execute_commands(chassis, 'local', rib_log_commands, rib_logs_file)
 
#SCP files back to pwd
call(['scp', '-r', username + '@' + hostname + ':/' + debug_dir, "."]) 
