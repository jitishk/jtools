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

global_commands             =[ 
                                'show clock',
                                'show system status detail',
                                'show process rib chunk-statistics',
                                'show process rib shared-memory-statistics',
                                'show ip route counters global',
                                'show ip route xcrp',
                                'show clock',
                            ] 

global_commands             =[ 
                                'show clock',
                                'show system status detail',
                                'show system status detail card all',
                                'show process rib thread-info',
                                'show process rcm thread-info',
                                'show process ism thread-info',
                                'show process tunnel thread-info',
                                'show process rib thread-history',
                                'show process rib chunk-statistics',
                                'show process rib shared-memory-statistics',
                                'show ipc process rib detail',
                                'show ipc process rcm detail',
                                'show ipc process ism detail',
                                'show ipc process tunnel detail',
                                'show ip route counters global',
                                'show ip route xcrp',
                                'show clock',
                            ] 

clear_logs_commands        = [
                                'clear ism log all',
                                'clear ip route log',
                            ]

show_logs_commands          = [
                                'show ip route log protocol 16 detail',
                                'show ip route log protocol 8 detail',
                                'show ip route log message detail',
                                'show ip route log config detail',
                                'show ip route log route detail',
                                'show ism client RIB log timestamp',
                                'show ism client static log timestamp',
                                'show ism client tunnel log timestamp',
                                'show ism client dot1q log timestamp',
                            ]


clients = {'bgp':80, 'static':16}

class jexec_cli_object(hltp_exec_cli_object):

    def __init__ (self, timeout=30, maxread=2000, searchwindowsize=None, logfilename=None):
        self.temp_logfile_read = None
        self.temp_logging = None
        self.logging = False

        if logfilename != None:
            self.logging = True
            self.logfile_read = open(logfilename, 'w')

        hltp_exec_cli_object.__init__(self)#timeout, maxread, searchwindowsize, None) 

    def set_logfile(self, logfilename, append=False):
        # Overwrite with new logging info 
        if logfilename == '' or logfilename == None:
            print ('Provide valid logfile')
            return
        if append == True:
            self.logfile_read = open(logfilename, 'a')
        else:
            self.logfile_read = open(logfilename, 'w')
        self.logging = True

    def override_logfile(self, logfilename, logging=True, append=False):
        # Store previous logging info 
        self.temp_logfile_read = self.logfile_read
        self.temp_logging = self.logging
        if logging == True:
            self.set_logfile(logfilename, append)
        else:
            self.logfile_read = None
            self.logging = False

    def revert_logfile(self):
        if self.logfile_read != None:
            self.logfile_read.close()
        self.logfile_read = self.temp_logfile_read
        self.logging = self.temp_logging
        self.temp_logfile_read = None
        self.temp_logging = None

    def close(self):
        if (self.logfile_read != None):
            self.logfile_read.close()
            self.logging = None
        if (self.temp_logfile_read != None):
            self.temp_logfile_read.close()
            self.temp_logging = None
        #hltp_exec_cli_object.close()

    def get_contexts(self):
        self.sendline('show context all')
        contexts_reply = self.read_until(prompt)
        exec_cli.expect_prompt(searchwindowsize=30)
        result_buf = self.before.split('\n')
        contexts = {}
        for line in result_buf:
            if line.find('0x400') > 0:
                contexts[line.split()[0].strip()] = line.split()[1].strip()

        return contexts


def gre_are_all_tunnels_up(exec_cli):

    exec_cli.sendline('show clock')
    exec_cli.sendline('show gre summary')
    exec_cli.expect_prompt(searchwindowsize=30)
    gre_summary = exec_cli.before
    print "GRE Summary: ", gre_summary

    total = int(gre_summary[gre_summary.find('total:') +
        len('total:'):gre_summary.find('up:')].strip())
    up = int(gre_summary[gre_summary.find('up:') +
        len('up:'):gre_summary.find('down:')].strip())
    if total == 0:
        print('Tunnels not configured yet')
        return (False, True)
    if up < total:
        print('%d tunnels up of %d' % (up, total))
        return (False, True)
    if up == total:
        print ('All tunnels UP %d' % up)
        return (False, False)
    if (up > total):
        print ('Error UP(%d) > TOTAL(%d)!!' % (up, total))
        return (True, False)

#
# Apply the configuration, given the config file.
#
def apply_config(config_file):
    py_err = True
    time_taken = -1
    chassis = hltp_exec_cli_object()

    if os.path.isfile(config_file):
        chassis.sendline('configure ' + config_file)
        chassis.expect_prompt(searchwindowsize=30)
        temp_buffer = chassis.before
        if temp_buffer.find('Error:') >= 0:
            print ('Errors applying config: ', config_file)
            print (temp_buffer)
            py_err = False
        elif temp_buffer.find('Configuration file processing took') >= 0:
            print (temp_buffer)
            temp_buffer = temp_buffer.split(':')
            time_taken = int(temp_buffer[1].split()[0])
            py_err = True
        else:
            print ('Could not find time taken to configure')
            print (temp_buffer)
            py_err = False
    else:
        print ('Config file not found: ', config_file)
        py_err = False
'''
            configure /flash/5gre-1.cfg
        Database lock contention detected
           globally locked for:
              Standby Synchronization
        Waiting to see if lock clears...

        Lock is cleared.


        Configuration complete
        % Configuration file processing took: 21 seconds
'''

    chassis.close()
    del chassis
    return (py_err, time_taken)

def make_dir(dir):
    exec_cli = hltp_exec_cli_object()
    exec_cli.sendline('mkdir ' + dir)
    exec_cli.expect_prompt()
    exec_cli.close()
    del exec_cli


def gre_test_case(ver, suffix, config_file_name):

    exec_cli = jexec_cli_object()

    debug_dir = '/md/riblogs/'
    exec_cli.sendline('mkdir ' + debug_dir)

    tc_file_name = debug_dir + '-'.join(['rib', 'gre', 'TC', str(ver)]) + '.' + '.'.join(['run', suffix])
    start_show_file_name = debug_dir + 'rib-global' + '-' +  str(ver) +  '-start' + '.show' + '.' + suffix
    end_show_file_name = debug_dir + 'rib-global' + '-' +  str(ver) +  '-end' + '.show' + '.' + suffix
    logs_file_name = debug_dir + '-'.join(['rib', 'ism', str(ver)]) + '.logs.' + '.'.join(['run', suffix])
    #config_file_name = '/flash/5gre-1.cfg'

    gre_poll_file_name = debug_dir + 'gre-polls-' + str(ver) + '.run.' + str(suffix)

    exec_cli.set_logfile(tc_file_name)
    exec_cli.sendline('echo "Starting TC"')
    exec_cli.sendline('show clock')
    exec_cli.sendline('echo "Collecting debugs"')
    exec_cli.expect_prompt(searchwindowsize=30)

    exec_cli.override_logfile(start_show_file_name)
    exec_cli.sendline('context local')
    for command in global_commands:
        exec_cli.sendline(command)
        exec_cli.expect_prompt(searchwindowsize=30)
    exec_cli.revert_logfile()

    #Clear all logs
    for command in clear_logs_commands:
        exec_cli.sendline(command)
        exec_cli.expect_prompt(searchwindowsize=30)

    # Apply GRE config
    exec_cli.sendline('echo "Applying Config"')
    exec_cli.sendline('show clock')
    (rc, time_taken) = apply_config(config_file_name)
    temp_line = 'Configuration Time Taken: ' + str(time_taken)
    exec_cli.sendline('echo "' + temp_line +'"')
    exec_cli.sendline('show clock')
    exec_cli.expect_prompt(searchwindowsize=30)

    # Poll tunnel up state
    MAX_POLL = 50
    count = 1
    rerun = True
    error = False
    exec_cli.override_logfile(gre_poll_file_name)
    while rerun == True and count < MAX_POLL:
        (error, rerun) = gre_are_all_tunnels_up(exec_cli)
        count += 1
        print 'Run: %d/%d' % (count, MAX_POLL)
        time.sleep(0.5)
    exec_cli.revert_logfile()

    temp_line = 'Polling Complete error=' + str(error) +', rerun=' + str(rerun) + ',count=' + str(count)
    exec_cli.sendline('echo "' + temp_line + '"')
    exec_cli.sendline('show clock')

    #Collect logs
    if rerun == False and error == False:
        exec_cli.override_logfile(logs_file_name)
        for command in show_logs_commands:
            exec_cli.sendline(command)
            exec_cli.expect_prompt(searchwindowsize=30)
        exec_cli.revert_logfile()

    #Collect final numbers
    if rerun == False and error == False:
        exec_cli.override_logfile(end_show_file_name)
        exec_cli.sendline('context local')
        for command in global_commands:
            exec_cli.sendline(command)
            exec_cli.expect_prompt(searchwindowsize=30)
        exec_cli.revert_logfile()

    exec_cli.sendline('echo "TC Done"')
    exec_cli.sendline('show clock')
    exec_cli.expect_prompt(searchwindowsize=30)
    exec_cli.close()
    del exec_cli
