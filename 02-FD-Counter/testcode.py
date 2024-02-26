# !/usr/bin/python3
import sys
from os import walk
from pathlib import Path
import subprocess
import re

import signal

p = re.compile("@fdcount: (\d+)")
fail_case_ctr = 0
total_case_ctr = 0

def __list_fds__ (procpath: Path) -> int:
    for (dirpath, dirnames, filenames) in walk(procpath):
        return len(filenames)

def __bpftrace_listing(pid:str) -> int:
    result = subprocess.check_output(['./FD-counter-pid.bt', pid])
    match = p.search(result.decode('utf-8'))
    if (match != None):
        return int(match.group(1))
    return 0

def print_test_result():
    global fail_case_ctr, total_case_ctr
    print ('\nTest Summary: Fails = ', fail_case_ctr, '/',total_case_ctr)

def signal_handler(sig, frame):
    print_test_result()
    sys.exit(0)

def __list_procs__ ():
    global fail_case_ctr, total_case_ctr
    for (dirpath, dirnames, filenames) in walk('/proc'):
        for dirs in dirnames:
            if dirs.isnumeric():
                pid = dirs
                fdinfo = Path('/proc/'+pid+'/fdinfo/')
                if (fdinfo.is_dir()):
                    total_case_ctr += 1

                    python_counted = __list_fds__(fdinfo)
                    bpf_counted = __bpftrace_listing(pid)
                    print("PID: %-8s fdinfo - python:%-4d bpf: %4d RESULT: " % (pid, python_counted, bpf_counted), end="")
                    if (python_counted != bpf_counted):
                        print (' !!! FAIL')
                        fail_case_ctr += 1
                    else:
                        print (' - PASS')
                else:
                    print('PID:',pid,'fdinfo NOT exists')
        break
    

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    __list_procs__()
    print_test_result()