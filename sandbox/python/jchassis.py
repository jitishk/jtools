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

class chassis_object(hltp_exec_cli_object):

    def __init__ (self, timeout=300, maxread=2000, searchwindowsize=30, logfilename=None):
        if logfilename != None:
            set_logfile_read(logfilename, False)
        hltp_exec_cli_object.__init__(self, timeout, maxread, searchwindowsize, None) 

    def close(self):
        if (self.logfile_read != None):
            self.logfile_read.close()
        hltp_exec_cli_object.close()

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

    def close_logfile(self)
        if self.logfile_read != None:
            self.logfile_read.close()

    def get_contexts(self):
        self.sendline('show context all')
        contexts_reply = self.read_until(prompt)
        self.expect_prompt()
        result_buf = self.before.split('\n')
        contexts = {}
        for line in result_buf:
            if line.find('0x400') > 0:
                contexts[line.split()[0].strip()] = line.split()[1].strip()
        return contexts

    def apply_config(self, config_file):
        error = False
        time_taken = -1

        if os.path.isfile(config_file) == False:
            print ('Config file not found: ', config_file)
            error = True
            return (error, time_taken)

        self.sendline('configure ' + config_file)
        self.expect_prompt()

        if self.buffer.find('Error:') >= 0:
            print ('Errors applying config: ', config_file)
            error = True
        elif (index = self.buffer.find('Configuration file processing took')) >= 0:
            temp_buffer = self.before[index:].split(':')
            time_taken = int(temp_buffer[1].split()[0])
            error = False
        elif self.buffer.find('Database lock') >= 0:
            print ('Database locked when applying config: ', config_file)
            error = True
        else:
            print ('Could not find time taken to configure')
            error = True
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

        print (self.before)
        return (error, time_taken)

