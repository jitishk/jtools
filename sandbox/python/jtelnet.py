#!/usr/bin/python

from subprocess import call
import sys
import pexpect
    

if len(sys.argv) < 3:
    print 'Usage: ' + sys.argv[0] + ' <ssr|se> <1-30> [log_file]'
    sys.exit()

platform = sys.argv[1]
number = sys.argv[2]
if int(number) < 10 and number > 0:
    number = '0'+ str(int(number))
elif int(number) > 30:
    print '%s Invalid chassis value; choose between 1-30' % number
    sys.exit()

log_file = ''
if(len(sys.argv) == 4):
    log_file = sys.argv[3]


def chassis_login(hostname, username, password):
    print 'Login into ' + hostname
    chassis = pexpect.spawn ('telnet ' + hostname)
    chassis.expect('login:')
    chassis.sendline (username)
    chassis.expect ('Password:')
    chassis.sendline (password)
    chassis.expect('\[local\]')
    chassis.sendline('en')
    chassis.sendline(password)
    chassis.expect('\[local\]')
    print 'Done'
    return chassis
 
hostname = 'sjl3-ecp-' + platform + str(number) + '.eld'
username = 'test'
password = 'test'

if len(log_file):
    call(['script', log_file + '.script'])

chassis = chassis_login(hostname, username, password)
chassis.interact()

if len(log_file):
    call(['exit'])


