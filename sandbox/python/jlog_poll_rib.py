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
                    "show clock",
                    "show ip route summary all",
                    "show ip route counters global",
    ]

if (sys.argv[1] == '-h'):
    print("\n")
    print(sys.argv[0] + ' '.join([' <hostname>','<when>','<how many times>','<how often>','<logfile>']))
    print("\nExample:")
    print(sys.argv[0] + ' '.join([' sjl3-ecp-ssr27.eld', '0','10','30','pdstats.log']))
    print("\n")
    sys.exit()

hostname = 'telnet ' + sys.argv[1]
when = int(sys.argv[2])
runs = int(sys.argv[3])
period = int(sys.argv[4])
logfilename = sys.argv[5]
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

time.sleep(when)
for i in range(0, runs):
    for command in commands:
        print ("\t" + command)
        exec_cli.sendline(command)
        exec_cli.expect(exec_cli_prompt)
    print ("\n")
    time.sleep(period)

exec_cli.logfile.close() 
exec_cli.close()
