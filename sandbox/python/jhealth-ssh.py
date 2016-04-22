#!/usr/bin/python
import os, telnetlib
import sys
import getpass
from subprocess import call

#Get commands
basic_commands_per_context  = [ 
                                "show clock",
                                "show ip route all",
                                "show ip route next-hop detail",
                                "show ip route registered next-hop",
                                "show ip route registered prefix",
                                "show ip route client",
                                "show ip route fib-client",
                            ]


global_commands             = [ 
                                "show clock",
                                "show ip route xcrp",
                                "show process rib ipc detail",
                                "show ipc process rib detail",
                                "show system status detail card all",
                                "show ip route counters global",
                                "show process rib thread-info",
                                "show process rib thread-history",
                                "show process rib chunk-statistics"
                            ]

rib_log_commands            = [ 
                                "show clock",
                                "show ip route log",
                                "show ip route log message detail",
                                "show ip route log config detail",
                                "show ip route log route detail"
                            ]
 
PORT = "23"
user = "test"
password = getpass.getpass()
hostname = "sjl3-ecp-ssr13"
hostip = "10.126.142.14"
hostname = "sjl3-ecp-ssr13"
hostip = "10.126.142.14"
hostname = "sjl3-ecp-ssr12"
hostip = "10.126.142.13"
hostname = "sjl3-ecp-ssr25"
hostname = "Ericsson"
hostip = "10.126.142.147"

disable_prompt = "[local]" + hostname + ">"
prompt = "[local]" + hostname + "#"
 
# dbg_file = open("in.log", "w")

def input_params(): 
    num_args = len(sys.argv)
    if(num_args == 1):
        print "Please provide host name, username, and password"
        sys.exit()

    index = 1
    for arg in sys.argv[1:num_args]:
        if (arg == "--chassis"):
            HOST = sys.argv[index+1]
        elif (arg == "--user"):
            user = sys.argv[index+1]
        elif (arg == "--password"):
            password = sys.argv[index+1]
        #else:
            #print "Unknown argument: %s" % arg 
        index = index + 1
    return (HOST, user, password)


def login_chassis(ip, user, password, host):
    print "telnet ", ip
    tn = telnetlib.Telnet(ip, PORT)
    print(tn.read_until("login: "))
    tn.write(user + "\n")
    print(tn.read_until("Password: "))
    tn.write(password + "\n")
    tn.read_until("[local]" + host)
    print "telnet Successful "
    tn.write("en\n")
    tn.write(password + "\n")
    #print(tn.read_until("[local]" + host + "#"))
    print(tn.read_until("[local]" + host) )
    print "Admin enabled"
    return tn


def get_contexts(tn):
    tn.write("show context all\n")
    contexts_reply = tn.read_until(prompt)
    contexts_reply = contexts_reply.split( )
    context_name = "local"
    contexts = {}
    for context_id in contexts_reply:
        if context_id.find("0x4008") >= 0:
            contexts[context_name] = context_id 
        else:
            context_name = context_id
    return contexts

EOD = "END_OF_DEBUG_COLLECTION"
def show_commands_in_context(tn, context_name, commands, file_name):
    context_prompt = "[" + context_name + "]" + hostname + "#"

    # Change context and start file
    command = "context " + context_name
    echo_command = 'echo "' + context_prompt + command + '"'
    tn.write(command + "\n")
    tn.write(echo_command + " | save " + file_name + "\n")

    # Execute each command in context
    for command in commands:
        echo_command = 'echo "' + context_prompt + command + '"'
        tn.write(echo_command + " | append " + file_name + "\n")
        tn.write(command + " | append " + file_name + "\n")

    # Detect end-of-execution
    # tn.write("echo " + EOD + "\n");
    # print(tn.read_until(EOD))
    tn.write("context local\n")
    return file_name

# (HOST, user, password) = input_params()

#Log into chassis
tn = login_chassis(hostip, "test", "test", hostname)

#Get contexts
contexts = get_contexts(tn)

print contexts

#Read route from all contexts
for context_name in contexts:
    context_file = "rib_" + context_name + ".show"
    show_commands_in_context(tn, context_name, basic_commands_per_context, context_file)
    call(["scp", user + "@" + hostip + "://md/" + context_file, "."]) 

#Execute global commands in local context
local_context = "local"
global_file = "rib_global.show"
show_commands_in_context(tn, local_context, global_commands, global_file)
call(["scp", user + "@" + hostip + "://md/" + global_file, "."]) 

#Execute show log commands in local context
local_context = "local"
rib_logs_file = "rib_logs.show"
show_commands_in_context(tn, local_context, rib_log_commands, rib_logs_file)
call(["scp", user + "@" + hostip + "://md/" + rib_logs_file, "."]) 
 
