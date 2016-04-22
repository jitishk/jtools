#!/usr/bin/python
import os
import sys
import pexpect

import getopt
import time

from subprocess import call


def chassis_login(hostname, username, password, logfilename):
    # Login into the chassis
    exec_cli_prompt = ['\[.+?\].+?#', '\[.+?\].+?>', 'login:', 'Password:', 'password'];
    ssh_command = 'ssh ' + username + '@' + hostname
    exec_cli = pexpect.spawn(ssh_command)
    exec_cli.logfile_read = open(logfilename, 'w')
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
    print ("Logged into " + hostname)
    return exec_cli
 

sshresp = 'Are you sure you want to continue connecting'

oprofile_start_commands = [
        'start sh',
        'su',
        'root',
        'opcontrol --deinit',
        'modprobe oprofile timer=1',
        'rm -rf /md/oprofile',
        'mkdir /md/oprofile',
        'opcontrol --start-daemon  --separate=lib,kernel,thread --vmlinux=/md/sfi.vmlinux --session-dir=/md/oprofile/session --callgraph=25',
#        'opcontrol --start-daemon  --separate=lib,kernel,thread --vmlinux=/md/vmlinux --image=/usr/lib/siara/bin/ribd --session-dir=/md/oprofile/session --callgraph=25',
        'opcontrol --start'
        ]
oprofile_end_commands = [
        'start sh',
        'su',
        'root',
        'opcontrol --dump',
        'opcontrol --stop',
        'opreport --session-dir=/md/oprofile/session --symbols --merge=tgid --debug-info --sort=app-name --global-percent --callgraph --output-file=/md/oprofile/callgraph',
        'opreport --session-dir=/md/oprofile/session --symbols --merge=tgid --debug-info --sort=app-name --accumulated --output-file=/md/oprofile/report',
        ]

if (sys.argv[1] == '-h'):
    print("\n")
    print(sys.argv[0] + ' '.join([' <hostname>', '<log.file>', '[start|end]']))
    print("\nExample:")
    print(sys.argv[0] + ' '.join([' sjl3-ecp-ssr27.eld', 'rib_global.log', 'start']))
    print("\n")
    sys.exit()

# Login into the chassis
username = 'test'
password = 'test'
hostname = sys.argv[1]
logfilename = sys.argv[2]
operation = sys.argv[3]
exec_cli = chassis_login(hostname, username, password, logfilename)

if operation == 'start':
    commands = oprofile_start_commands
elif operation == 'end':
    commands = oprofile_end_commands

exec_cli_prompt = ['\[.+?\].+?#', 'sh-3\.2\$', 'bash-3.2#', 'Password'];
for command in commands:
    command = command.strip()
    print ("\t" + command)
    exec_cli.sendline(command)
    exec_cli.expect(exec_cli_prompt, timeout=300)

if operation == 'end':
    call(['scp', '-r', 'test@' + hostname + '://md/oprofile/', '.'])

exec_cli.close()
