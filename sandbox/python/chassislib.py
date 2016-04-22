#!/usr/bin/python

import pexpect

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

