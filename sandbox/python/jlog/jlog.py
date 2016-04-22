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

'''

[10:25am] [sandbox/python/jlog]> before (last 100 chars): Trying
10.126.142.15...
Badly placed ()'s.
[10:26am] [sandbox/python/jlog]> telnet: connect to address 10.126.142.15:
No route to host
'''

if (sys.argv[1] == '-h'):
    print("\n")
    print(sys.argv[0] + ' '.join([' <hostname>', '<log.file>', '<commands.file>']))
    print('or')
    print(sys.argv[0] + ' '.join([' <hostname>', '<log.file>', '<commands.file>', '<when>', '<how many times>', '<how often>']))

    print("\nExample:")
    print(sys.argv[0] + ' '.join([' sjl3-ecp-ssr27.eld', 'rib_global.log', 'global.commands']))
    print('or')
    print(sys.argv[0] + ' '.join([' sjl3-ecp-ssr27.eld', 'rib_global.log', 'global.commands', '0', '10', '60']))
    print("\n")
    sys.exit()

hostname = 'telnet ' + sys.argv[1]
logfilename = sys.argv[2]
commands_file = sys.argv[3]
when = 0
runs = 1
period = 0
if len(sys.argv) > 4:
    when = int(sys.argv[4])
    runs = int(sys.argv[5])
    period = int(sys.argv[6])


f = open(commands_file)
commands = list(f)# .readlines()
f.close()

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

# After enabling admin, we dont need '[.+?\].+?>'...it conflicts with 'show system stat
# detail
#exec_cli_prompt = ['\[.+?\].+?#', 'login:', 'Password:', 'sh-3\.2\$', pexpect.EOF];
#exec_cli_prompt = ['\[local\].+?\#', 'login:', 'Password:', 'sh-3\.2\$'];

#[local] administrator: (test) logged in via tty: /dev/pts/1, host:

time.sleep(when)
print ("Executing commands")
for run in range(0, runs):
    for command in commands:
        command = command.strip()
        print ("\t" + command)
        exec_cli.sendline(command)
        exec_cli.expect(exec_cli_prompt, timeout=30, searchwindowsize=30)
    time.sleep(period)

exec_cli.logfile.close() 
exec_cli.close()
