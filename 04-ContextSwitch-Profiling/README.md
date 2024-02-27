# BCC: Execve Syscall vs Pid statistics

## Question
Write a BCC program to measure the average time taken by processes in the system (context switch time = difference between the time when the second process starts and the first process stops).

**Expected Deliverable**: A single file with your code that outputs min, max and mean of the context switch
time (the output should appear when Ctrl+C is pressed after running your program).

## Solution

Command invocation invocation
```shellscript
$ sudo /bin/python contextswitch-monitor.py
```

Example invocation:
```shellscript
$ sudo /bin/python contextswitch-monitor.py
Profiling scheduler... Hit Ctrl-C to end.
^C
Test Summary: Context Switch Latency stats: 
         min =  540 ns 
         max =  291290009 ns 
         avg =  1095045.679850108 ns 
         event count =  24551
```

## BUG Observations

### PerfEventArray exception

On exiting program with Ctrl+C, at times, the bellow exception is noted:

```
Exception ignored on calling ctypes callback function: <function PerfEventArray._open_perf_buffer.<locals>.raw_cb_ at 0x7fd0d99e6de0>
Traceback (most recent call last):
   File "/usr/lib/python3/dist-packages/bcc/table.py", line 980, in raw_cb_
     def raw_cb_(_, data, size):
```
This seem to be due to https://github.com/iovisor/bcc/issues/3049, but program functionality is not affected.

### Abnormal timestamp values returned from bpf_ktime_get_ns

Randomly the time delta calculation which are using bpf_ktime_get_ns() seems to be returning abnormal values. For which as of now, the high values are skiped in code and the below print is issued to note the instance occurance.

```
sudo /bin/python contextswitch-monitor.py
Profiling scheduler... Hit Ctrl-C to end.
TASK/BUG: VERY HIGH value cpu 2 ctx-switch-lat: 225376064640449 ns


TASK/BUG: VERY HIGH value cpu 10 ctx-switch-lat: 225376066279896 ns

KeyboardInterrupt: 
^C
Test Summary: Context Switch Latency stats: 
         min =  600 ns 
         max =  545235653 ns 
         avg =  7500022.037298493 ns 
         event count =  9491
```

## Test code

TODO
