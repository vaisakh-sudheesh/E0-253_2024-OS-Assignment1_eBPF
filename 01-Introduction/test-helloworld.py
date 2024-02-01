#!/usr/bin/python
import os
import subprocess

tracefile = open("/sys/kernel/debug/tracing/trace_pipe", "r")
ctr = 10
found = False
while (ctr > 0):
    subprocess.run(["ls", "-l"])
    value = str(os.read(tracefile.fileno(),1024))
    if (value.find("bpf_trace_printk: Hello World!!!") != -1):
        found = True
        break
    ctr = ctr - 1

if (found):
    print ("Test completed succesfully...")
else:
    print ("Test failed!!!")

