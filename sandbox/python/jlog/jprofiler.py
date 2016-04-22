#!/usr/bin/python
import os
import sys
import pexpect

import getopt
import time

username = 'test'
password = 'test'

def exec_shell(exec_cli):
    if exec_cli == Null:
        return

sshresp = 'Are you sure you want to continue connecting'

oprofile_start_commands = [
        'start sh',
        'su',
        'root',
        'opcontrol --deinit',
        'modprobe oprofile timer=1',
        'opcontrol --start  --separate=lib,kernel,thread --vmlinux=/md/vmlinux --image=/usr/lib/siara/bin/ribd --session-dir=/md/oprofile-results',
        ]
oprofile_end_commands = [
        'start sh',
        'su',
        'root',
        'opcontrol --dump',
        'opcontrol --stop',
        'opreport --session-dir=/md/oprofile-results --symbols --callgraph --output-file=/md/oprofile.callgraph',
        'opreport --session-dir=/md/oprofile-results --symbols --output-file=/md/oprofile.report ',
        ]

if (sys.argv[1] == '-h'):
    print("\n")
    print(sys.argv[0] + ' '.join([' <hostname>', '<log.file>', '[start|end]']))
    print("\nExample:")
    print(sys.argv[0] + ' '.join([' sjl3-ecp-ssr27.eld', 'rib_global.log', 'start']))
    print("\n")
    sys.exit()

hostname = 'telnet ' + sys.argv[1]
logfilename = sys.argv[2]
operation = sys.argv[3]

exec_cli_prompt = ['\[.+?\].+?#', '\[.+?\].+?>', 'login:', 'Password:',
'sh-3\.2\$', 'bash-3.2'];

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
exec_cli.sendline('start sh')
exec_cli.expect(exec_cli_prompt)
exec_cli.sendline('su')
exec_cli.expect(exec_cli_prompt)
exec_cli.sendline('root')
exec_cli.expect(exec_cli_prompt)

if operation == 'start':
    commands = oprofile_start_commands
elif operation == 'end':
    commands = oprofile_end_commands

for command in commands:
    command = command.strip()
    print ("\t" + command)
    exec_cli.sendline(command)
    exec_cli.expect(exec_cli_prompt, timeout=300)

exec_cli.logfile.close() 
exec_cli.close()
