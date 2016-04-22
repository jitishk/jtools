#!/usr/bin/python

# TODO
# rib_handle_clr_cnt_info detects next_rtp: as caller. next_rtp is a goto label.

from subprocess import check_call
import commands
import sys

class Func:
    name = ''           # Name of function
    callers = []        # Array of all calling functions
    definition = ''     # Stores file and line # of definition
    declarations = []   # Array of all file and line#s of declarations

    def __init__(self, name):
        self.name = name

    def add_caller(self, calling_func_name):
        self.callers.append(call_func_name)

def get_callers(func_name, prefix):
    if trace.has_key(func_name):
        print ("Here")
        return
    else:
        trace[func_name] = 1

    callers = {}
    command = 'grep -Ircl --include=*.{c,cpp,h} "\<' + func_name + '\>" *'.strip()
    command = 'grep -Ircl --include=*.{c} "\<' + func_name + '\>" *'.strip()
    files = commands.getoutput(command).strip()
    print (prefix + func_name)

    for file in files.split('\n'):

        # Use gcc -E option to preprocess the .c file.
        command = 'gcc -E ' + file + ' > temp'
        commands.getoutput(command)

        command = 'grep -n "\<' + func_name + '\>" temp'.strip()
        refs = commands.getoutput(command).strip()
        print(refs)

        # Sometimes the func name may be in a comment. So the first grep detects
        # it in a file, but the second grep returns empty. Ignore these files
        if refs.strip() == '':
            continue

        lines = open('temp', 'r').readlines()
        for ref in refs.split('\n'):
            ref = ref.strip().split(':')
            ref_ln = int(ref[0])-1      #Line number of reference, translate to 0 index
            max_ln = len(lines)

            # Determine if the function name occurence (reference) is a call,
            # definition or declaration. 
            # If there is a '{', in this or subsequent lines, then its a definition.
            # If there is a ';', in this or subsequent lines, then its a declaration
            # or call. Then check to see if any parameter to the function (between the '()') has
            # space between them. If yes, it is a declaration, else a call.
            # TODO: Handle void function calls and declarations
            definition = declaration = call = thread_call = False
            ln = ref_ln - 1
            line = ''
            print (ref_ln, ln)
            while ln >= 0:
                if lines[ln].strip().find(';') >= 0 or lines[ln].strip().find('{') >= 0:
                    break;
                line += lines[ln].strip()
                ln -= 1

            ln = ref_ln
            while ln < max_ln :
                line += lines[ln].strip();
                if line.find('{') >= 0:
                    eol = True
                    definition = True
                    #print ("Definition: " + line);
                    break;
                elif line.find(';') >= 0:
                    try:
                        parameters = line.split('(')[1].split(',')
                        if parameters[0].strip().find(' ') > 0:
                            #print ("Declaration: " + line);
                            declaration = True
                        else:
                            #print ("Call: " + line);
                            call = True
                            if line.strip().find('spawn') >= 0:
                                thread_call = True
                                thread_callers[func_name] = 1
                    except:
                        print ('Exception:' +  line)
                        sys.exit(1)
                    break;
                ln += 1

            if call == True and thread_call == False:
                # Find out the calling function
                ln = ref_ln
                while ln >= 0:
                    line = lines[ln]
                    ln -= 1
                    if line.startswith(' ') or line.startswith('\t') or line.startswith('{') or line.strip() == '' or line.startswith('#'):
                        # Ignore indented, empty, lines that starts with '{',
                        # or with '#' indicating preprocessor instructions.
                        continue
                    else:
                        caller = line.split('(')[0].strip()
                        #print ("caller: " + caller)
                        if callers.has_key(caller):
                            callers[caller] += 1
                        else:
                            callers[caller] = 1
                        #callers.append(caller)
                        break

    for func in callers.keys():

        get_callers(func, prefix + '  ')

    return callers
trace = {}
thread_callers = {}
func_name = "rib_update_path_nh_back_chain"
func_name = sys.argv[1]
func = Func(func_name)
depth = 0
prefix = ''
callers = get_callers(func_name, prefix)

print (thread_callers)

'''
for func in callers.keys():
    print get_callers(func)

print (callers)
'''



