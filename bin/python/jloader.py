#!/usr/bin/python

import getopt
import os
import pexpect
import sys

import jchassis

signum = os.environ['USER']

def print_usage (verbose=False):
    print 'jloader <chassis-name> [-h] [-u username/password] [-i image]'

user = 'test'
pwd = 'test'
chassis_name = ''
commands = []
image = ''
 
if len(sys.argv) < 2 or sys.argv[1].strip() == '-h' or sys.argv[1] == '--help':
    print_usage()
    sys.exit()

# Get chassis name from arguments to script
chassis_name = sys.argv[1]
#TODO learn to do mkstemp
logfile_name = chassis_name + '-jloader.jlog'

# Set other options
try:
    opts, args = getopt.getopt(sys.argv[2:],"hu:i:", ["help=", "user-pwd=", "image="])
except getopt.GetoptError:
    print_usage()
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-h", "--help"):
        print_usage()
        sys.exit()
    elif opt in ("-u", "--user-pwd"):
        user = arg.strip().split('/')[0].strip();
        password = arg.strip().split('/')[1].strip();
        # TODO check format for user/pwd
    elif opt in ("-i", "--image"):
        image = arg.strip()
        # TODO Check if image exists and requires to be scp'ed
        # TODO check for sdk
 
def choose_image_from_legacy ():
    ## List images from /scratch/testimages/<signum>
    cli_prompt = ['password', '\[' + signum + '@.*\]'];
    lxapp_server = 'lxapp-3.sj.us.am.ericsson.se'
    ssh_command = 'ssh ' + signum + '@' + lxapp_server

    #TODO try catch to handle bad prompts
    cli = pexpect.spawn(ssh_command)
    index = cli.expect(cli_prompt)
    if index == 0:
        linux_password = getpass.getpass(signum + '@' + lxapp_server + ' password:')
        exec_cli.sendline(linux_password)
        exec_cli.expect(cli_prompt)

    cli.sendline('cd /scratch/testimages/' + signum)
    cli.expect(cli_prompt)
    cli.sendline('ls *.tar.gz | xargs')
    cli.expect(cli_prompt)
    cli.close()

    images = cli.before.split('\r\n')[1].split()

    index = 0
    for image in images:
        print ('[' + str(index) + '] ' + image)
        index += 1
    index = input('index: ')
    image = images[index]
    return image

if not image:
    image = choose_image_from_legacy()

# instantiate a chassis
chassis = jchassis.jchassis(chassis_name, logfilename=logfile_name)

chassis.login(username=user, password=pwd)

#Release download the image
chassis.load(image)

chassis.close()

