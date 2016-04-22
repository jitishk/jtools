#!/usr/bin/python
import ConfigParser, os
import sys
import re
import subprocess
import datetime
import time
import getopt
from string import split

def usage():
    print '''

    \033[1myssrsim - deploy SSR-SIM deployments of various size

Usage - yssrsim [--help] [--beam-me-up-scotty] <ini file>\033[0m

yssrsim builds up a full SSR-SIM deployment using a configuration INI file,
including preparation of the SDK, creation of the topology (chassis, cards,
wiring), copying files, custom built libraries and binaries, loading of the
binaries and execution of a given script. The topology can contain
multiple chassis, potentially of different versions with varying setup.

The setup of the deployment includes the copying of RSA keys onto the RPSWs
to setup passwordless login and the modification of the SSH configuration in
the HUB to allow seamless work with the simulated SSRs from the HUB directly.

Multiple executions of the script with the same setup will leave the existing
deployment intact, only adding the possible extra differences and recopying
the specified files, libs and binaries, reloading the binaries and reexcuting
the autorun script.

\033[1mCommandline arguments\033[0m

\033[1m--beam-me-up-scotty\033[0m - after the deployment start one xterm
        for each RPSW with SSH onto the RPSW and exec_cli started
\033[1m--help\033[0m - print usage information instead of deploying

\033[1mConfiguration file format\033[0m

The configuration file uses the regular INI file format.

The major sections and their configuration items:

\033[1m[general]\033[0m - general configuration items of the deployment

\033[1mSIM host\033[0m - the SSR-SIM host machine (mandatory parameter)
\033[1musername\033[0m - the user ID on the SSR-SIM host machine (optional defaults
        to user ID on the local machine)
\033[1mbasename\033[0m - the basename used for naming chassis and cards, it can contain
        %VERSION% (SDK version), %USER% (user ID) and %DATE% (current date)
        variables (optional parameter, defaults to %VERSION%)
\033[1mkeyfile\033[0m - the path to the authorized keys file which would be used on
        the SSR-SIM RPSWs to setup passwordless SSH access to them, one use case where
        one would want to define a specific keyfile is when one wants to allow access
        to multiple people, those people's keys could be stored in a keyfile and used
        during deployment (optional parameter, defaults to ~/.ssh/id_rsa.pub)
\033[1mcleanup script\033[0m - the generated cleanup script file's path, it tears down
        the deployment, excluding the removal of the SDKs (optional, if omitted
        no cleanup script is generated)
\033[1mautorun script\033[0m - a script which should be run after the deployment setup
        has finished, for example to automatically run some tests, commandline
        arguments can be listed freely (optional)


\033[1m[global config]\033[0m - skeleton of the chassis, items defined here would be

        used for each chassis if not overriden explicitly (also for some
        parameters chassis specific values can be appended to the global config
        instead of full replacement if the parameter is prefixed with '+' in
        the specific chassis's definition)
\033[1mcards\033[0m - the specific cards in the chassis, one card per line, first
        the card type, then the slot (as used in SSR-SIM), separated by
        whitespace (optional, if omitted chassis will be empty)
\033[1mversion\033[0m - the version of the SDK, can be %PROJ% which would automatically
        resolve to the version extracted from the current git repository
        (in this case the current working directory has to be somewhere in 
        a git repository), or it can be given explicitly (with the leading 'v' 
        omitted), the value of version is used as %VERSION% in the basename
        (optional, defaults to %PROJ%)
\033[1mimage\033[0m - the SDK image, it could be either 'sysbuild', then the sysbuild
        image of the specified version would be used or it can be a path
        to a custom built SDK image (optional, defaults to sysbuild),
        %PROJ% can be used in the path
\033[1mwhitelist binaries\033[0m - custom built binaries which should be loaded onto
        the simulated SSR, one binary per line, if a process should be also
        restarted, then the binary name should be be followed by the process
        name too, separated with whitespace (optional)
\033[1mwhitelist libraries\033[0m - custom built libraries which should be loaded onto
        the simulated SSR, list of .so filenames, separated with whitespace (optional)
\033[1mcopy\033[0m - files which should be copied onto the simulated SSR (usually cfg files),
        one per line, for each the local path and remote path should be given,
        separated by whitespace, instead of files directories can be also specified
        (optional), paths relative to the root of the git repository can be
        specified by using %PROJ% as the beginning of the path, %CHASSIS_ID% can be used
        in the path and will be replaced with the defined chassis ID for each chassis


\033[1m[chassis]\033[0m - individual chassis definitions, one section can cover multiple
        chassis which will have the same configuration but different names, all
        the parameters from [global config] are valid and allow chassis specific
        override of the global values, all of them are optional (and default
        to the global setup), if one is prefixed with '+' the global value and
        the local will be concatenated (for example copy of a file is specified
        globally and copy of another file is specified locally,
        but using '+' -> both files will be copied), such concatenation is valid
        for all [global config] parameters except version and image

\033[1mid\033[0m - the ID of the individual chassis which should be created, the chassis
        are named the following way: <basename>_<chassis id> and the cards are
        named: <lower case slot name>_<basename>_<chassis id>, for example if
        the basename is %USER% which resolves to the userid of 'eabcdef' and
        the specific chassis's ID is 1 and an rpsw is specified for slot RPSW1,
        then the chassis's name is 'eabcdef_1' and the rpsw name is
        'rpsw1_eabcdef_1' (mandatory)


\033[1m[wiring]\033[0m - wiring specs

\033[1mbridge\033[0m - bridge specs, one per line, in the form of
         <bridge name> - <end point 1>  - <end point 2> , the bridge name will
         be used in the SSR-SIM, the end point definition format is
         the following: <chassis id>/<slot>/<port> , where the chassis id is
         the short id used in the INI file


\033[1mKnown issues, shortcomings:\033[0m
- the tool expects that if a card with the generated name already exists it's of
  the right type and located in the right slot
- the tool expects that the slot for a given card is empty (or that the given
  card occupies it and in such case no new card has to be created)
- the tool expects that if a bridge with the specified name already exists it
  has the right setup
- the tool expects that the specifed ports on the specified cards are free and
  can be wired with the specified bridge if the bridge itself has to be created
- strange error from the SDK's ssr-sim-rootops.exp when copying the RSA key to
  a VM where it's already present (it's more of a noise then a real issue)'''

def remove_extra_ws(s):
    return ' '.join(s.replace('\n', ' ').split())

def cmd_with_output(c):
    return subprocess.Popen(c, stdout=subprocess.PIPE, shell=True).stdout.read()

def cmd(c):
   print c
   return subprocess.call(c, shell=True)

def resolve_vars_except_version(config):
    s = config.get('general', 'basename')
    u = config.get('general', 'username')
    return s.replace('%DATE%', datetime.date.today().strftime('%d%m%Y')).replace('%USER%', u)

def get_version(s):
    if config.get(s, 'version') == '%PROJ%':
        # FIXME - not robust enough, what if currently accidentally in a git
        # repo which is not an official repo
        if cmd("git describe 2>/dev/null") != 0:
            print 'No explicit version was given and not in a git repository, thus aborting'
            sys.exit()
        version = split(cmd_with_output("git describe")[1:-1], '-', 1)[0]
        config.set(s, 'version', version)

    return config.get(s, 'version')

def chassis_exists(host, user, chassis):
    # FIXME ugly, how robust?
    return cmd_with_output('ssh %s@%s ls /var/ssr-sim-uselist/chassis/*/ | grep "^%s\.%s"' % (user, host, chassis, user)) != ''

def card_exists(host, user, card):
    # FIXME ugly, how robust?
    return cmd_with_output('ssh %s@%s ls /var/ssr-sim-uselist/card/*/ | grep "^%s\.%s"' % (user, host, card, user)) != ''

def bridge_exists(host, user, bridge):
    # FIXME ugly, how robust?
    return cmd_with_output('ssh %s@%s ls /var/ssr-sim-uselist/bridge/ | grep "^%s\.%s"' % (user, host, bridge, user)) != ''

def path_exists(host, user, path):
    return cmd('ssh %s@%s ls %s 1>/dev/null 2>/dev/null' % (user, host, path)) == 0 

def prepare_ssrsim(host, user, version, image, proj_dir):
    sdk_dir = '/ssrsim/%s/ssr-sdk/v%s' % (user, version)
    if not path_exists(host, user, sdk_dir):
        print '\033[1mPreparing SDK %s (%s image) on %s at %s\033[0m' % (version, image, host, sdk_dir)
        if image != 'sysbuild':
            if re.match('%PROJ%', image):
                if proj_dir:
                    image = image.replace('%PROJ%', proj_dir)
                else:
                    print 'You have defined the SDK image path relative to your project path, but you are not in a project directory (GIT repository)'
                    sys.exit()
            remote = '/ssrsim/%s/%s' % (user, os.path.basename(image))
            cmd('scp %s %s@%s:%s' % (image, user, host, remote))
            cmd('ssh %s@%s python prepsdk.py %s %s' % (user, host, version, remote))
        else:
            cmd('ssh %s@%s python prepsdk.py %s' % (user, host, version))
    else:
        print '\033[1mSDK at %s on %s already exists, skipping SDK preparation\033[0m' % (sdk_dir, host)

def create_chassis(host, user, ssr_sim, id, section, config, card_map, rpsws, new_rpsws, cleanup_commands):
    chassis_name = '%s_%s' % (config.get(section, 'basename'), id)

    if not chassis_exists(host, user, chassis_name):
        print '\033[1mCreating chassis %s\033[0m' % chassis_name
        cmd('ssh %s@%s %s create chassis %s' % (user, host, ssr_sim, chassis_name))
    else:
        print '\033[1mChassis %s already exists\033[0m' % chassis_name

    cleanup_commands.append('%s delete %s' % (ssr_sim, chassis_name))

    for card in config.get(section, 'cards').split('\n'):
        [card_type, slot] = card.split(' ')
        card_name = '%s_%s' % (slot.lower(), chassis_name)
        if card_type == 'rpsw':
            rpsws.add(card_name)
        card_map['%s/%s' % (id, slot.lower())] = [chassis_name, card_name]

        if not card_exists(host, user, card_name):
            print '\033[1mCreating card %s (%s) and inserting it into slot %s of chassis %s\033[0m' % (card_name, card_type, slot, chassis_name)
            cmd('ssh %s@%s %s create %s %s' % (user, host, ssr_sim, card_type, card_name))
            # FIXME - what if slot already occupied?
            cmd('ssh %s@%s %s insert %s %s %s' % (user, host, ssr_sim, card_name, chassis_name, slot))
            if card_type == 'rpsw':
                new_rpsws.add(card_name)
        else:
            # FIXME - what if card exists, but not inserted into the chassis?
            print '\033[1mCard %s already exists\033[0m' % card_name

        cleanup_commands.append('%s delete %s %s' % (ssr_sim, card_type, card_name))
        cleanup_commands.append('%s remove %s %s %s' % (ssr_sim, card_name, chassis_name, slot))

    cleanup_commands.append('%s stop %s' % (ssr_sim, chassis_name))

    chassis_on = cmd_with_output('ssh %s@%s cat /var/ssr-sim-uselist/chassis/*/%s.%s | grep STAT' % (user, host, chassis_name, user)).split('=')[1][:-1] == 'ON'
    if not chassis_on:
        # ssr-sim start waits for the user to press something, which blocks the python script, hence this proxy shell script
        cmd('ssh %s@%s ./ssrsim-start.sh %s %s' % (user, host, ssr_sim, chassis_name))
        delay = 90
        print "Waiting for %s secs while the chassis boots up" % delay
        time.sleep(delay)
    else:
        print "Chassis already running"

def create_wiring(host, user, ssr_sim, config, card_map, cleanup_commands):
    if not config.has_section('wiring'):
        print 'No [wiring] section specified, skipping'
        return
    if not config.has_option('wiring', 'bridge'):
        print 'No bridge item under [wiring] section specified, skipping'
        return
    for bridge in config.get('wiring', 'bridge').split('\n'):
        bridge_items = map(str.strip, bridge.split('-'))

        bridge_name = bridge_items[0]
        # An alternative for bridge naming? Instead of explicit naming use hash of a
        # systematically generated name (unfortunately bridge names are capped at 12 chars)
        # bridge_name = str(hash('bridge-%s_%s_%s-%s_%s_%s' % (chassis1, slot1, port1, chassis2, slot2, port2)))
        # bridge_name = 'br%s' % bridge_name[-10:len(bridge_name)]

        if not bridge_exists(host, user, bridge_name):
            print '\033[1mSetting up bridge %s\033[0m' % bridge_name
            cmd('ssh %s@%s %s create bridge %s' % (user, host, ssr_sim, bridge_name))
        else:
            print '\033[1mBridge %s already exists, adding in missing wires\033[0m' % bridge_name

        cleanup_commands.append('%s delete bridge %s' % (ssr_sim, bridge_name))

        for end_point in bridge_items[1:]:
            # FIXME - if existing bridge occupies the port, tear it down
            [chassis, slot, port] = map(str.strip, end_point.split('/'))
            [chassis_name, card] = card_map['%s/%s' % (chassis, slot)]
            cmd('ssh %s@%s %s wireup %s %s port:%s' % (user, host, ssr_sim, bridge_name, card, port))
            cleanup_commands.append('%s wiredown %s %s port:%s' % (ssr_sim, bridge_name, card, port))

def setup_ssh(host, user, ssr_sim, rpsw):
    print '\033[1mSetting up convenient SSH for %s (passwordless login and Host entry in ~/.ssh/config)\033[0m' % rpsw
    cmd('ssh %s@%s %s scp %s:/tmp/ id_rsa.pub' % (user, host, ssr_sim, rpsw))
    ssh_port = cmd_with_output('ssh %s@%s cat /var/ssr-sim-uselist/card/rpsw/%s.%s | grep SSHP' % (user, host, rpsw, user)).split('=')[1][:-1]
    ret = cmd("ssh %s@%s './ssrsim-ssh-copy-id-exp' %s /tmp/id_rsa.pub" % (user, host, ssh_port))
    if ret == 0:
        # FIXME convenient, but ugly
        cmd('echo "\nHost %s\n'
                   'User root\n'
                   'Hostname %s\n'
                   'Port %s\n'
                   'StrictHostKeyChecking no\n'
                   'UserKnownHostsFile /dev/null" >> ~/.ssh/config' % (rpsw, host, ssh_port))
    return ret

def copy_stuff(list, rpsw, proj_dir, id):
    for i in list:
        if i == '':
            continue
        [src, dst] = i.split(' ')
        src = src.replace('%CHASSIS_ID%', id)
        if re.match('%PROJ%', src):
            if proj_dir:
                src = src.replace('%PROJ%', proj_dir)
            else:
                print 'Not in a git repository, skipping %s' % src
                continue
        if os.path.isdir(src):
            cmd('scp -r %s %s:%s' % (src, rpsw, dst))
        else:
            cmd('scp %s %s:%s' % (src, rpsw, dst))

def copy_whitelist_libraries(list, rpsw, proj_dir):
    script_path = os.path.dirname(os.path.realpath(__file__))
    print '\033[1mCopying libraries for replacement\033[0m'
    for line in list:
        for lib in line.split(' '):
            cmd('%s/ssrsim-copy-whitelists.sh %s %s lib %s' % (script_path, rpsw, proj_dir, lib))

def copy_whitelist_binaries(list, rpsw, proj_dir):
    script_path = os.path.dirname(os.path.realpath(__file__))
    print '\033[1mCopying binaries for replacement\033[0m'
    for bin in list:
        b = bin.split(' ')
        if len(b) == 2:
            cmd('%s/ssrsim-copy-whitelists.sh %s %s bin %s %s' % (script_path, rpsw, proj_dir, b[0], b[1]))
        else:
            cmd('%s/ssrsim-copy-whitelists.sh %s %s bin %s' % (script_path, rpsw, proj_dir, b[0]))

# dict variant for ConfigParser to be able to separate multiple [chassis] sections
# with unique IDs internally instead of the default merging behaviour
class multichassis_dict(dict):
    _unique = 0

    def __setitem__(self, key, val):
        if isinstance(val, dict) and key == 'chassis':
            self._unique += 1
            key += str(self._unique)
        dict.__setitem__(self, key, val)

# --- actual execution starts from here ---

start = datetime.datetime.now()
        
config = ConfigParser.ConfigParser(None, multichassis_dict)

opts, args = getopt.getopt(sys.argv[1:], "", ["beam-me-up-scotty", "help"])

if ((("--help", "") in opts) or (len(args) != 1)):
    usage()
    sys.exit()

config.read(args[0])

print 'Processing %s config' % args[0]

# process [general]

general_defs = [['SIM host', None],
                ['username', os.getenv('USER')],
                ['basename', '%VERSION%'],
                ['keyfile', '~/.ssh/id_rsa.pub'],
                ['cleanup script', ''],
                ['autorun script', '']]

if not config.has_section('general'):
    print '\033[1mMandatory [general] section is not specified\033[0m'
    sys.exit()
for i in general_defs:
    try:
        config.get('general', i[0])
    except ConfigParser.NoOptionError, err:
        if i[1] == None:
            print "\033[1m[general] %s manadatory but not specified!\033[0m" % i[0]
            sys.exit()
        else:
            config.set('general', i[0], i[1])

config.set('general', 'basename', resolve_vars_except_version(config))

# process [global config]

if not config.has_section('global config'):
    config.add_section('global config')

# name, default, appendable (can append to global config with '+' prefix instead of replace) 
global_config_defs = [['cards', '', True], 
                      ['copy', '', True],
                      ['image', 'sysbuild', False],
                      ['version', '%PROJ%', False],
                      ['whitelist binaries', '', True],
                      ['whitelist libraries', '', True]]

for i in global_config_defs:
    try:
        config.get('global config', i[0])
    except ConfigParser.NoOptionError, err:
        if i[1] == None:
            print "\033[1m[global config] %s mandatory but not specified!\033[0m" % i[0]
            sys.exit()
        else:
            config.set('global config', i[0], i[1])

version = get_version('global config')

# process [chassis]

card_map = dict()
ssr_sim = ''
host = config.get('general', 'SIM host')
user = config.get('general', 'username')
keyfile = config.get('general', 'keyfile')

if not os.path.exists(os.path.expanduser(keyfile)):
    print "\033[1mSSH public keyfile %s missing, but it is required for setting up passwordless login for RPSWs, aborting, you can specify other keyfile with the 'keyfile' option in the [general] section\033[0m" % keyfile
    sys.exit()

# collect clean up pair of each setup command as the setup is progressing and
# at the end reverse the list as tear down is done exactly the opposite order as the setup
cleanup_commands = [] 

# general prep
script_path = os.path.dirname(os.path.realpath(__file__))
cmd('scp %s %s@%s:id_rsa.pub' % (keyfile, user, host))
cmd('scp %s/prepsdk.py %s@%s:' % (script_path, user, host))
cmd('scp %s/ssrsim-start.sh %s@%s:' % (script_path, user, host))
cmd('scp %s/ssrsim-ssh-copy-id-exp %s@%s:' % (script_path, user, host))

# autorun script from [general]
autorun_script = config.get('general', 'autorun script')

proj_dir = None
# FIXME - not robust enough, what if currently accidentally in a git repo which is not an official repo
if cmd('git rev-parse --show-toplevel 2>/dev/null') == 0:
    proj_dir = cmd_with_output('git rev-parse --show-toplevel')[:-1]

all_rpsws = set()

for s in config.sections():
    if re.match('chassis', s):
        try:
            config.get(s, 'id')
        except ConfigParser.NoOptionError, err:
            print "id not specified in %s section!" % s
            sys.exit()

        # fill in missing parts from [global config]
        for i in global_config_defs:
            try:
                config.get(s, i[0])
            except ConfigParser.NoOptionError, err:
                config.set(s, i[0], config.get('global config', i[0]))
            try:
                v = config.get(s, '+%s' % i[0])
                if i[2]:
                    config.set(s, i[0], '%s\n%s' % (config.get('global config', i[0]), v))
                else:
                    '%s at the global config and chassis level can not be combined, only replaced, hence ignoring this config item'
            except ConfigParser.NoOptionError, err:
                None

        version = get_version(s)

        prepare_ssrsim(host, user, version, config.get(s, 'image'), proj_dir)
        ssr_sim = '/ssrsim/%s/ssr-sdk/v%s/sdk/scripts/ssr-sim' % (user, version)

        config.set(s, 'basename', config.get('general', 'basename').replace('%VERSION%', version))

        ids = remove_extra_ws(config.get(s, 'id')).split()
        for id in ids:
            rpsws = set()
            new_rpsws = set()
            create_chassis(host, user, ssr_sim, id, s, config, card_map, rpsws, new_rpsws, cleanup_commands)
            for rpsw in new_rpsws:
                setup_ssh(host, user, ssr_sim, rpsw)
            for rpsw in rpsws:
                all_rpsws.add(rpsw)
                copy_stuff(config.get(s, 'copy').split('\n'), rpsw, proj_dir, id)
                if proj_dir:
                    # FIXME - would be more compact without ssrsim-copy-whitelists.sh
                    cmd("echo '' > ./.ssrsim-proc-rest")
                    copy_whitelist_libraries(config.get(s, 'whitelist libraries').split('\n'), rpsw, proj_dir)
                    copy_whitelist_binaries(config.get(s, 'whitelist binaries').split('\n'), rpsw, proj_dir)
                    # load binaries
                    update = 'true' if rpsw not in new_rpsws else 'false'
                    cmd('%s/setup-ssrsim-ssh %s %s %s %s' % (script_path, rpsw, './.ssrsim-proc-rest', update, autorun_script))
                    cmd('rm ./.ssrsim-proc-rest')
                else:
                    print 'Not in a git repository, skipping whitelist library and binary copying'

# process [wiring]

# no idea whether SDK version can affect wiring and what should be done when we would like to
# wire multiple chassis of different versions, so just picking one SDK version and using it
create_wiring(host, user, ssr_sim, config, card_map, cleanup_commands)

# create cleanup script
if config.get('general', 'cleanup script') != '':
    f = open(config.get('general', 'cleanup script'), 'w')
    cleanup_commands.reverse()
    f.write('\n'.join(cleanup_commands))
    f.close()

stop = datetime.datetime.now()
runtime = stop - start
print "\033[1mDuration: %s:%s (m:s)\033[0m" % (runtime.seconds / 60, str(runtime.seconds % 60).zfill(2))

if ("--beam-me-up-scotty", "") in opts:
    for rpsw in all_rpsws:
        cmd("xterm -title '%s' -e ssh %s /usr/lib/siara/bin/exec_cli -nx &" % (rpsw, rpsw))
