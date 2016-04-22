#!/usr/bin/python
import os
import sys
import pexpect

import getpass
import getopt
import time



from subprocess import call

signum = os.environ['USER']
default_commands = [
                    'show version',
                    'show release',
                    'show process rib detail',
                    'show process rib ipc',
                    'show process rib thread-info',
                    'show ip route counters global',
            ]
 
class jchassis:

    def __init__ (self, chassisname, logfilename='temp.jlog', append=False):
        if chassisname.strip() == '':
            print 'Chassis name cannot be empty. '
            sys.exit(2)
        self.chassisname = chassisname.strip()
        self.logfilename = logfilename.strip()
        self.logfileappend = append;
        # TODO cleanup prompts. Let each def have its own prompt
        self.cli_prompts = [
                '^login:',
                'Password:',
                'password',
                'Are you sure you want to continue connecting \(yes\/no\)\?',
                'RSA host key for ',
                'Permission denied, please try again',
                '\[.+?\].+?>',
                '\[.+?\].+?#',
                'Bad Password',
            ]
        self.commands = default_commands;
        self.when = 0
        self.runs = 1
        self.period = 0

    def login (self, username='test', password='test'):
        if not username.strip() or not password.strip():
            print 'user/password %s/%s cannot be empty. Defaulting to test/test' % (username, password)

        print "Logging into %s@%s" % (username, self.chassisname)
        ssh_command = 'ssh ' + username + '@' + self.chassisname
        try:
            self.cli = pexpect.spawn(ssh_command)
            if self.logfileappend == True:
                self.cli.logfile_read = open(self.logfilename, 'a')
            else:
                self.cli.logfile_read = open(self.logfilename, 'w')

            while True:
                index = self.cli.expect(self.cli_prompts)
                if index == 0:
                    self.cli.sendline(username)
                elif index == 1:
                    self.cli.sendline(password)
                elif index == 2:
                    self.cli.sendline(password)
                elif index == 3:
                    self.cli.sendline('yes')
                elif index == 4:
                    print ('RSA host key changed, removing key for '+self.chassisname+' from /home/'+signum+'/.ssh/known_hosts')
                    # TODO: Find a more robust way to find this line. Especially
                    # the condition below
                    # eussjlxxen208 234432/aug08> ssh test@esv-ssr-006.eld
                    # Warning: the RSA host key for 'esv-ssr-006.eld' differs
                    # from the key for the IP address '10.126.142.174'
                    # Offending key for IP in /home/ejitkol/.ssh/known_hosts:74
                    # Matching host key in /home/ejitkol/.ssh/known_hosts:83
                    # Are you sure you want to continue connecting (yes/no)?
                    #
                    hostkey_line = self.cli.before.strip().splitlines()[19].strip().split(':')[1].strip()

                    # Remove the offending key from the known hosts file
                    call(["sed",  "-i", hostkey_line + "d", "/home/" + signum + "/.ssh/known_hosts"])

                    # Try to spawn the ssh session again.
                    print ('Trying to ssh to %s again' % self.chassisname)
                    self.cli = pexpect.spawn(ssh_command)
                    if self.logfileappend == True:
                        self.cli.logfile_read = open(self.logfilename, 'a')
                    else:
                        self.cli.logfile_read = open(self.logfilename, 'w')
                elif index == 5:
                    print ('Permission denied, %s/%s does have access' % (username, password))
                    sys.exit(2)
                elif index == 6:
                    self.cli.sendline('en')
                elif index == 7:
                    self.cli.sendline('terminal length 0')
                    self.cli.expect(self.cli_prompts)
                    break
                elif index == 8:
                    print self.cli_prompts[index] + ": " + password
                    sys.exit(2)
                    break


        except pexpect.EOF:
            print "Exception EOF occured when logging to chassis"
            print "Before: ", self.cli.before
            print "After: ", self.cli.after   
            print "Match: ", self.cli.match
            sys.exit()
        except pexpect.TIMEOUT:
            print "Exception TIMEOUT occured when logging to chassis"
            print "Before: ", self.cli.before
            print "After: ", self.cli.after
            sys.exit()
        print ("Logged into " + self.chassisname)

    def execute (self, commands=None):
        if commands == None:
            commands = self.commands
        time.sleep(self.when)
        print ("Executing commands")
        try:
            for self.run in range(0, self.runs):
                for command in commands:
                    command = command.strip()
                    print ("\t" + command)
                    self.cli.sendline(command)
                    self.cli.expect(self.cli_prompts, timeout=10, searchwindowsize=60)
                time.sleep(self.period)
        except pexpect.EOF:
            print "Exception EOF occured when executing " + command
            print "Before: ", self.cli.before
            print "After: ", self.cli.after   
            print "Match: ", self.cli.match
        except pexpect.TIMEOUT:
            print "Exception TIMEOUT occured when executing " + command
            print "Before: ", self.cli.before
            print "After: ", self.cli.after   

    def load (self, image):
        print "Loading image /scratch/testimages/%s/%s" % (signum,  self.chassisname)
        prompts = [
                '\[.+?\].+?#',
                'password',
                'Are you sure you wish to erase this release\? \(y\/n\)',
                'Do you want to cancel the download in progress \(y\/n\)\?',
                'Release erase failed',
                'Not all cards are ready, download abort',
                'Distributing release on alternate partition ...',
                'Installation failed.'
            ]
        command = 'release download ftp://' + signum + '/'.join(['@10.10.10.22//scratch/testimages', signum, image])
        print ('Executing: ', command)
        self.cli.sendline(command)
        while True:
            index = self.cli.expect(prompts, timeout=1800, searchwindowsize=60)
            if index == 0:
                break
            elif index == 1:
                ftp_password = getpass.getpass('Enter ftp password for ' + signum + '@10.10.10.22: ')
                self.cli.sendline(ftp_password)
            elif index == 2:
                self.cli.sendline('y')
            elif index == 3:
                print ('Release download already in progress...')
                ans = input(prompts[index])
                self.cli.sendline(ans)
                return
            elif index == 4:
                print (prompts[index], 'aborting...')
                print self.cli.before, self.cli.match, self.cli.after
                return
            elif index == 5:
                print (prompts[index])
                print ('Sleeping for 1 min')
                time.sleep(60)
                self.cli.sendline(command)
                print ('Executing: ', command)
            elif index == 6 or index == 7:
                print (prompts[index])

        print "Loading complete"    

    def close (self):
        self.cli.sendline('exit')
        self.cli.logfile_read.close()
        self.cli.close()

