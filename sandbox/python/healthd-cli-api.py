#
# 05/07/2012
#
#    Copyright (c) 2012 Ericsson AB.
#    All rights reserved.
#


import sys
import decimal
import operator
import string
import re
from SSR.SWRP.cli import hltp_exec_cli
from SSR.SWRP.cli.hltp_show_context import *
from SSR.SWRP.cli.hltp_show_ip_route import *
from SSR.SWRP.cli.hltp_show_card import *
from generic.actions.hltp_gen_TS import *

import time

#Commands

def healthd_show_cli(context_name, commands, file_name=''):
    """
        Execute a list of commands in a particular context. The results are
        copied to a file if provided. Else the output is printed out.

        Input:
            context_name    : Context in which the commands will be executed
            commands        : List of CLI commands that will be executed
            file_name       : Name of file to which the result of commands
                              will be stored. 
        Returns:
            None

        Usage:
            e.g. execute_commands('local', global_commands, 'debug.logs')
    """

    # Create chassis object and set file for logs
    try:
        chassis = hltp_exec_cli_object()
    except:
        print "error"
        return
    if file_name <> ''):
        chassis.logfile_read = file(file_name, 'w')
        to_file = True


    # Change context and start file
    chassis.sendline('context ' + context_name)
    chassis.expect_prompt()
    if to_file == False:
        print chassis.before

    # Execute each command in context
    for command in commands:
        print 'Command: ' + command
        chassis.sendline(command)
        chassis.expect_prompt()
        if to_file == False:
            print chassis.before

    # close file and chassis object
    if to_file == True:
        chassis.logfile_read.close()

    chassis.close()
    del chassis

def get_contexts():
    try:
        chassis = hltp_exec_cli_object()
    except:
        print "error"
        return None

    chassis.sendline('show context all')
    contexts_reply = chassis.read_until(prompt)
    chassis.expect_prompt()
    result_buf = chassis.before.split('\n')
    contexts = {}
    for line in result_buf:
        if line.find('0x400') > 0:
            contexts[line.split()[0].strip()] = line.split()[1].strip()

    return contexts

def execute_commands_in_all_contexts(chassis = None, commands, filename = None):
    contexts = get_contexts()
    for context in contexts:
        healthd_show_cli(context, commands


EOD = "END_OF_DEBUG_COLLECTION"

def gre_check_if_tunnels_are_up():
    '''
        Checks if all GRE tunnels have come up. The information is obtained from
        the cli command 'show gre summary'.
    '''

    chassis = hltp_exec_cli_object()
    chassis.logfile_read = file(debug_dir + 'gre-polls.log', 'a')
    chassis.sendline('show clock')
    chassis.expect_prompt()
    chassis.sendline('show gre summary')
    chassis.expect_prompt()
    gre_summary = chassis.before
    print "gre summary: ", gre_summary

    total = int(gre_summary[gre_summary.find('total:') +
            len('total:'):gre_summary.find('up:')].strip())
    up = int(gre_summary[gre_summary.find('up:') +
            len('up:'):gre_summary.find('down:')].strip())
    if total == 0:
        # The tunnels have not been configured yet. 
        print "Tunnels not configured yet"
        return (False, True)
    if up < total:
        print "%d tunnels up of %d" % (up, total)
        return (False, True)
    if up == total:
        print "All tunnels UP %d" % up
        return (False, False)
    if (up > total):
        print 'Error UP(%d) > TOTAL(%d)!!' % (up, total)
        return (True, False)

    # close file and chassis object
    chassis.logfile_read.close()
    chassis.close()
    del chassis

#
# Apply the configuration, given the config file.
#
def apply_config(config_file):
    py_err = True
    time_taken = -1
    chassis = hltp_exec_cli_object()

    if os.path.isfile(config_file):
        chassis.sendline('configure ' + config_file)
        chassis.expect_prompt(600)
        temp_buffer = chassis.before
        if temp_buffer.find('Error:') >= 0:
            print 'Errors applying config: ', config_file
            print temp_buffer
            py_err = False
        elif temp_buffer.find('Configuration file processing took') >= 0:
            temp_buffer = temp_buffer.split(':')
            time_taken = int(temp_buffer[1].split()[0])
            py_err = True
        else:
            print 'Could not find time taken to configure'
            print temp_buffer
            py_err = False
    else:
        print 'Config file not found: ', config_file
        py_err = False

    chassis.close()
    del chassis
    return (py_err, time_taken)


def gre_test_case(ver, suffix):
    chassis = hltp_exec_cli_object()
    if chassis.is_ready() == False:
        print "Could not get CLI prompt"
        return 
    file_name = debug_dir + '-'.join(['rib', 'gre', 'TC', str(ver)]) + '.' + '.'.join(['run', suffix])
    chassis.logfile_read = file(file_name, 'w')

    chassis.sendline('echo "Starting TC"')
    chassis.sendline('show clock')
    chassis.sendline('mkdir ' + debug_dir)

    context = 'local'
    file_name = debug_dir + '-'.join(['rib', 'global', context, str(ver), 'start']) + '.' + '.'.join(['show', suffix])
    execute_commands('local', global_commands, file_name) 

    # Apply GRE config
    chassis.sendline('echo "Applying Config"')
    chassis.sendline('show clock')
    (rc, time_taken) = apply_config('/flash/16k-1.cfg')
    temp_line = 'Configuration Time Taken: ' + str(time_taken)
    chassis.sendline('echo "' + temp_line +'"')
    chassis.sendline('show clock')
    print 'Time taken: ', time_taken

    # Poll tunnel up state
    MAX_POLL = 60
    count = 1
    rerun = True
    error = False
    while rerun == True and count < MAX_POLL:
        (error, rerun) = gre_check_if_tunnels_are_up()
        count += 1
        time.sleep(5)
    print 'rerun: ', rerun
    print 'error: ', error 
    print 'count: ', count
    temp_line = 'Polling Complete error=' + str(error) +', rerun=' + str(rerun) + ',count=' + str(count)
    chassis.sendline('echo "' + temp_line + '"')
    chassis.sendline('show clock')
    chassis.sendline('echo "Polling complete"')

    if rerun == False and error == False:
        # Get the final status, all configured tunnels are UP
        file_name = debug_dir + '-'.join(['rib', 'global', context, str(ver), 'end']) + '.' + '.'.join(['show', suffix])
        execute_commands('local', global_commands, file_name) 

    chassis.expect_prompt()
    chassis.logfile_read.close()
    chassis.close()
    del chassis
