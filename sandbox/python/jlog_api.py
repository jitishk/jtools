#!/usr/bin/python
import os
import sys
import pexpect

import getopt
import time


def exec_shell(exec_cli):
    if exec_cli == Null:
        return
logfilename = 'cli.log'
when = 0
runs = 4
period = 3
hostname = 'telnet sjl3-ecp-ssr27.eld'
username = 'test'
password = 'test'
command = 'pidstat -r'

if (sys.argv[1] == '-h'):
    print("\n")
    print(sys.argv[0] + ' '.join([' <hostname>','<shell_command>','<when>','<how many times>','<how often>','<logfile>']))
    print("\nExample:")
    print(sys.argv[0] + ' '.join([' sjl3-ecp-ssr27.eld','"pidstat -r"','0','10','30','pdstats.log']))
    print("\n")
    sys.exit()

print (sys.argv)
hostname = 'telnet ' + sys.argv[1]
command = sys.argv[2]
when = int(sys.argv[3])
runs = int(sys.argv[4])
period = int(sys.argv[5])
logfilename = sys.argv[6]

exec_cli_prompt = ['\[.+?\].+?#', '\[.+?\].+?>', 'login:', 'Password:', 'sh-3\.2\$'];

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

time.sleep(when)
exec_cli.sendline('start sh')
exec_cli.expect(exec_cli_prompt)
print (exec_cli.before)

for i in range(0, runs):
    exec_cli.sendline('pidstat -r')
    exec_cli.expect(exec_cli_prompt)
    print (exec_cli.before)
    time.sleep(period)

exec_cli.logfile.close() 
exec_cli.close()
