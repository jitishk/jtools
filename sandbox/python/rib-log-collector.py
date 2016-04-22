#
# 05/07/2012
#
#    Copyright (c) 2012 Ericsson AB.
#    All rights reserved.
#


import sys
import decimal
import operator
import string
import re
from SSR.SWRP.cli import hltp_exec_cli
from SSR.SWRP.cli.hltp_show_context import *
from SSR.SWRP.cli.hltp_show_ip_route import *
from SSR.SWRP.cli.hltp_show_card import *
from generic.actions.hltp_gen_TS import *

#Commands
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
                                "show clock",
                                "show ip route log",
                                "show ip route log message detail",
                                "show ip route log config detail",
                                "show ip route log route detail"
                            ]

rib_log_config              = [
                                'config',
                                'context local',
                                'ip route log route size 65535',
                                'ip route log message size 65535',
                                'end'
                            ]

clients = {'bgp':80}
 
#
# This is a wrapper for hltp_ping_debug() to invoke the function in the
# troubleshoot thread context
#
def rib_debug_start(dest_ip, context):
    """
       Debug ping failure to a particular ip address (Troubleshoot thread)

       Input:
           dest_ip: Destination ip address to check.
           context: Context to check

       Returns:
           True: if no errors found.
           False: if errors found. 

       Usage:
           healthd_ping_debug(dest_ip, context):
           e.g. healthd_ping_debug('10.1.1.1', 'local' ) will debug
           ping failure for ip address 10.1.1.1 in context local and display
           if there are any errors. 
    """
    temp_cmd = ["rib_collect_logs()"]
    healthd_troubleshoot("".join(temp_cmd))



def rib_config_log_protocol(exec_cli, protocol_name, size):
    config = [ 
        'config',
        'context local',
        'ip log protocol ' + clients[protocol_name] + ' size ' + size,
        'end'
    ]
    for config_line in config:
        exec_cli.sendline(config_line)
        exec_cli.expect_prompt()
    
base_clients = [
    'connected',
    'adjacency',
    'ip host',
    'subscriber address',
    'subscriber static',
    'subscriber dummy',
    'subscriber dhcp-pd',
    'subscriber nd',
    'aggregate'
]

def rib_find_protocol_id(exec_cli, protocol_name, context):
    exec_cli.sendline('show ip route client')
    exec_cli.expect_prompt()
    buffer = exec_cli.before
    buffer = buffer.split('\n')
    for line in buffer:
        line = line.strip().split(' ', 1)
        if(len(line) and line[0] == protocol_name):
            id = line[1].split('(',1)[1].split('/',1)[0]
            return id

def execute_commands(context_name, commands, file_name = 'default.show'):
    # Create chassis object and set file for logs
    debug_dir = '/md/riblogs/'
    chassis = hltp_exec_cli_object()
    chassis.sendline('mkdir ' + debug_dir)
    filep = file(debug_dir + file_name, 'w')
    chassis.logfile_read = filep

    # Change context and start file
    chassis.sendline('context ' + context_name)
    chassis.expect_prompt()

    # Set terminal length to 0
    chassis.sendline('terminal length 0')
    chassis.expect_prompt()

    # Execute each command in context
    for command in commands:
        print 'Command: ' + command
        chassis.sendline(command)
        chassis.expect_prompt()
    # Switch back to local context befor exiting function
    chassis.sendline('context local')
    chassis.expect_prompt()

    # close file and chassis object
    filep.close()
    chassis.close()


'''
# Spawn exec_cli
exec_cli = hltp_exec_cli.hltp_exec_cli_object()
if exec_cli.is_ready() == False:
    print("FAIL - Could not get CLI prompt")
    sys.exit()
else:
    print("OK")

exec_cli.sendline('show clock')
exec_cli.expect_prompt()
temp_buffer = exec_cli.before
print(temp_buffer)

#context = 'local'
#exec_cli.sendline('context ' + context)
#exec_cli.expect_prompt()
#bgp_id = rib_find_protocol_id(exec_cli, 'bgp', context)

#exec_cli.sendline('show ip route client ' + bgp_id + ' detail')
#exec_cli.expect_prompt()
#temp_buffer = exec_cli.before
#print(temp_buffer)
'''
