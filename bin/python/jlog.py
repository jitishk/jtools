#!/usr/bin/python

import jchassis
from jcommands import get_commands_to_configure_logs
from jcommands import get_commands_to_flush_logs

import sys, getopt

def get_commands_syslog ():
    commands= [
            'show version',
            'show release',
            'show clock',
            'show system status detail',
            'show process rib detail',
            'show process rib ipc detail',
            'show process rib ipc-pack-statistics',
            'show process rib shared-memory-statistics',
            'show process rib shmm',
            'show process rib thread-info',
            'show process rib thread-history',
            'show process rib chunk-statistics',
            'show process rib xtimer',
            'show process rib pal statistics',
            'show ip route global',
            'show ip route summary all',
            'show ip route counters global',     
            'show crashfiles',
            'show log | grep RIB-',
]       
    return commands   

def print_usage (verbose=False):
    print '\njlog <chassis-name> [-u username/password] [-l <logfilename>] [-a/--append] [-s/--syslogs] [-f <commands-file>] [-c/--config-logs <comma-separated slots>] [-e/--flush-logs]'
    print '\ne.g. jlog sjl-ecp-ssr10.eld -u test/test -l temp.log --config-logs 1,4,7\n'

append_log_flag = False;
user = 'test'
pwd = 'test'
chassis_name = ''
log_file = 'temp.jlog'
commands = []
 
if len(sys.argv) < 2 or sys.argv[1].strip() == '-h' or sys.argv[1] == '--help':
    print_usage()
    sys.exit()

# Get chassis name from arguments to script
if len(sys.argv) < 2:
    print_usage()
    sys.exit(2)
chassis_name = sys.argv[1]

# Set other options
try:
    opts, args = getopt.getopt(sys.argv[2:],"hu:l:asf:c:e", ["help", "user-pwd=", "log-file=", "append", "syslogs", "commandsfile-name=", "config-logs=", "flush-logs"])
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
        # check format for user/pwd
    elif opt in ("-l", "--logfile-name"):
        log_file = arg
    elif opt in ("-a", "--append"):
        append_log_flag = True
    elif opt in ("-s", "--syslogs"):
        syslog_flag = True
        commands.extend(get_commands_syslog())
    elif opt in ("-c", "--config-logs"):
        slots = arg.strip().split(',')
        commands.extend(get_commands_to_configure_logs(route=1000, config=1000, msg=1000, eof=1000, slots=slots, ingress=1000, egress=1000))
    elif opt in ("-e", "--flush-logs"):
        commands.extend(get_commands_to_flush_logs())
    elif opt in ("-f", "--commandsfile-name"):
        commands_file = arg
        # Check if commands file exists
        fp = open(commands_file)
        commands.extend(list(fp))
        fp.close()

if commands == []:
    print "No commands provided...exiting"
    sys.exit()

# instantiate a chassis
chassis = jchassis.jchassis(chassis_name, log_file, append_log_flag)

# log into chassis
chassis.login(username=user, password=pwd)

if append_log_flag == True:
    commands.insert(0, 'echo "Next run of logs"')
print commands

chassis.execute(commands)

chassis.close()


