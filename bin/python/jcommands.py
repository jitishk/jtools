#!tusr/bin/python

def get_commands_to_configure_logs (route=0, config=0, msg=0, eof=0, slots=[], ingress=0, egress=0):
    commands = [
            'config',
            'context local',
            'ip global-flags dont-log-src-query',
    ]
    if route > 0:
        commands.append('ip log route size ' + str(route))
    if msg > 0:
        commands.append('ip log message size ' + str(msg))
    if config > 0:
        commands.append('ip log config size ' + str(config))
    if eof > 0:
        commands.append('ip log eof size ' + str(eof))
    for slot in slots:
        if ingress > 0:
            commands.append('ip log slot ' + str(slot) + ' ingress size ' + str(ingress))
        if egress > 0:
            commands.append('ip log slot ' + str(slot) + ' egress size ' + str(egress))

    commands.append('ip global-flags log-to-file-reopen')
    commands.append('ip global-flags log-to-file')
    commands.append('commit')
    return commands

def get_commands_to_flush_logs ():
    commands = [
            'config',
            'context local',
            'ip global-flags log-to-file-reopen',
            'commit',
    ]
    return commands
 

def get_commands_to_collect_logs (route=True, msg=True, config=False, slots=[]):
    commands = ['terminal length 0']

    if route == True:
        commands.append('show ip route log route detail')
    if msg == True:
        commands.append('show ip route log message detail')
    if config == True:
        commands.append('show ip route log config detail')
    for slot in slots:
        commands.extend([
            'show ip route log slot ' + str(slot) + ' ingress',
            'show ip route log slot ' + str(slot) + ' egress'
            ])

    return commands

def get_commands_for_prefix_to_and_from_rib (prefix, fabl_slots=[], ppa_slots=[]):
    commands = ['show clock']
    if prefix.find(':') == -1:
        commands.append('show ip route ' + prefix + ' detail')
        for slot in fabl_slots:
            commands.extend([
               'show card ' + str(slot) + ' fabl fib route ipv4 ' + prefix + ' detail',
               'show card ' + str(slot) + ' fabl fib route ipv4 ' + prefix + ' hidden'
            ])
        for slot in ppa_slots:
            commands.extend([
               'show card ' + str(slot) + ' ppa fib ' + prefix + ' detail',
               'show card ' + str(slot) + ' ppa fib ' + prefix + ' hidden',
            ]) 
    else:
        commands.append('show ipv6 route ' + prefix + ' detail')
        for slot in fabl_slots:
            commands.extend([
               'show card ' + str(slot) + ' fabl fib route ipv6 ' + prefix + ' detail',
               'show card ' + str(slot) + ' fabl fib route ipv6 ' + prefix + ' hidden'
            ]) 
        for slot in ppa_slots:
            commands.extend([
               'show card ' + str(slot) + ' ppa ipv6 fib ' + prefix + ' detail',
               'show card ' + str(slot) + ' ppa ipv6 fib ' + prefix + ' hidden',
            ]) 

    commands.append('show ip route log route detail | join-lines | grep ' + prefix)

    for slot in fabl_slots:
        commands.append('show card ' + str(slot) + ' fabl fib log rib ingress hidden | begin after 1 ' + prefix)
    for slot in ppa_slots:
        commands.append('show card ' + str(slot) + ' ppa fib log hidden | begin after 1 ' + prefix)

    return commands

def get_commands_syslog ():
    commands= [
            'show version',
            'show release',
            'show clock',
            'show process rib detail',
            'show process rib ipc detail',
            'show process rib thread-info',
            'show ip route counters global',
        ]       
    return commands

def get_coverity_commands (branch='swfeature_int', committed=False):

    commands = 'cov-private-build --web --verbose --branch ' + branch

    if committed == True:
        commands += ' --modified-files "`git diff HEAD~1 HEAD --name-only --relative | xargs echo`" gmake PRODUCT=ASG-RP'
    else:
        commands += ' --modified-files "`git diff --name-only --relative | xargs echo`" gmake PRODUCT=ASG-RP'

    return commands
