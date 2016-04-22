#!/usr/bin/python
import os
import sys
import pexpect

import getopt
import time


def exec_shell(exec_cli):
    if exec_cli == Null:
        return

commands = [
                    'show clock',
                    'show bgp summary',
                    'show proc bgp thread-info',
                    'show process rib detail',
                    'show process rib ipc detail',
                    'show process rib ipc-pack-statistics',
                    'show process rib shared-memory-statistics',
                    'show process rib shmm',
                    'show process rib ipc detail',
                    'show process rib thread-info',
                    'show process rib thread-history',
                    'show process rib chunk-statistics',
                    'show system status process ribd',
                    'show ip route global',
                    'show ip route summary all',
                    'show ip route counters global',
                    'show ip route xcrp'
                    'show sysstat sa sa1 | save /flash/sys_sa.txt'
                    'show sysstat pid pid1 | save /flash/sys_pid.txt'
                    'show system status detail' 
                    'show system status merged' 
                    'show log' 
                    'rcm-debug' 
                    'rdb-debug' 
                    'show ism gen' 
                    'show ism global' 
                    'show tech ism'
                    'show tech'
        ]

if (sys.argv[1] == '-h'):
    print("\n")
    print(sys.argv[0] + ' '.join([' <hostname>', '<logfile>']))
    print("\nExample:")
    print(sys.argv[0] + ' '.join([' sjl3-ecp-ssr27.eld', 'rib_global.log']))
    print("\n")
    sys.exit()

hostname = 'telnet ' + sys.argv[1]
logfilename = sys.argv[2]
username = 'test'
password = 'test'

exec_cli_prompt = ['\[.+?\].+?#', '\[.+?\].+?>', 'login:', 'Password:', 'sh-3\.2\$'];

# Login into the chassis
print (hostname)
exec_cli = pexpect.spawn(hostname)
exec_cli.logfile = open(logfilename, 'w')
exec_cli.expect(exec_cli_prompt)
exec_cli.sendline(username)
exec_cli.expect(exec_cli_prompt)
exec_cli.sendline(password)
exec_cli.expect(exec_cli_prompt)
exec_cli.sendline('en')
exec_cli.expect(exec_cli_prompt)
exec_cli.sendline(password)
exec_cli.expect(exec_cli_prompt)
exec_cli.sendline('terminal length 0')
exec_cli.expect(exec_cli_prompt)

print ("Executing commands")
for command in commands:
    print ("\t" + command)
    exec_cli.sendline(command)
    exec_cli.expect(exec_cli_prompt)

exec_cli.logfile.close() 
exec_cli.close()
