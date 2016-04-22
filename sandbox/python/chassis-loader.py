#!/usr/bin/python
import os
import sys
import getpass
from subprocess import call

import pexpect

num_args = len(sys.argv)
if(num_args == 1):
    print "Please provide host name, and version"
else:
    hostname = sys.argv[1]
    version = sys.argv[2]

def chassis_load_image(chassis, image):
    print "Loading %s with %s" % (chassis, image)
    release_download = 'release download ftp://ejitkol@10.10.10.22/' + image
    print(release_download)
    chassis.sendline(release_download)
    password = getpass.getpass()
    chassis.expect('password:')
    chassis.sendline(password)
    chassis.expect('Are you sure you wish to erase this release')
    chassis.sendline('y')
    chassis.expect('\[local\]')
    print 'Done'



hostname = 'sjl3-ecp-ssr' + hostname + '.eld'
chassis = pexpect.spawn ('telnet ' + hostname)
chassis.expect('login:')
chassis.sendline ('test')
chassis.expect ('Password:')
chassis.sendline ('test')
chassis.sendline('en')
chassis.sendline('test')
chassis.expect('\[local\]')
chassis.sendline('terminal length 0')
chassis.expect('\[local\]')
chassis.sendline('show ip route all | append rib_log.show')
chassis.expect('\[local\]')
print chassis.before
image = '/archive/build-images/REL_IPOS_13_1_114/SEOS-ASG-pkg-SSR-13.1.114.0.265.tar.gz'

chassis_load_image(hostname, image)


