# BCC: Execve Syscall vs Pid statistics

## Question
Write a BCC program to measure the average time taken by processes in the system (context switch time = difference between the time when the second process starts and the first process stops).

**Expected Deliverable**: A single file with your code that outputs min, max and mean of the context switch
time (the output should appear when Ctrl+C is pressed after running your program).


## Solution Approach
Most of the scheduler functionality in kernel resides in **kernel/sched/core.c**.

Though the core function for scheduling in **__schedule**, it is marked as notrace, there by preventing tracing via external frameworks.

```c
static void __sched notrace __schedule(unsigned int sched_mode)
```

Instead for tracking scheduler activities **schedule** is chosen as monitoring point.
```c
asmlinkage __visible void __sched schedule(void)
{
	struct task_struct *tsk = current;

	sched_submit_work(tsk);
	do {
		preempt_disable();
		__schedule(SM_NONE);
		sched_preempt_enable_no_resched();
	} while (need_resched());
	sched_update_worker(tsk);
}
EXPORT_SYMBOL(schedule);
```

Since the goal is to track  average time taken by processes in the system to perform context switch the duration about mentioned routine need to be track. For doing so, **kprobe** and **kretprobe** functionality of eBPF is utilized. per CPU core latency of entry exit is calculated and summarized as stated in the problem.

## Testing Command

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

## EBPF BUG Observations

### PerfEventArray exception

On exiting program with Ctrl+C, at times, the bellow exception is noted:

```
Exception ignored on calling ctypes callback function: <function PerfEventArray._open_perf_buffer.<locals>.raw_cb_ at 0x7fd0d99e6de0>
Traceback (most recent call last):
   File "/usr/lib/python3/dist-packages/bcc/table.py", line 980, in raw_cb_
     def raw_cb_(_, data, size):
```

```
sudo /bin/python /home/vaisakh/developer/OS/ebpf/assignment/E0-253_2024-OS-Assignment1_eBPF/04-ContextSwitch-Profiling/contextswitch-monitor.py
Profiling scheduler... Hit Ctrl-C to end.
TASK/BUG: VERY HIGH value cpu 14 ctx-switch-lat: 225303036736645 ns


^CException ignored on calling ctypes callback function: <function PerfEventArray._open_perf_buffer.<locals>.raw_cb_ at 0x7f5b7deead40>
Traceback (most recent call last):
  File "/usr/lib/python3/dist-packages/bcc/table.py", line 980, in raw_cb_
    def raw_cb_(_, data, size):

KeyboardInterrupt: 
^CException ignored on calling ctypes callback function: <function PerfEventArray._open_perf_buffer.<locals>.raw_cb_ at 0x7f5b7deeaca0>
Traceback (most recent call last):
  File "/usr/lib/python3/dist-packages/bcc/table.py", line 980, in raw_cb_
    def raw_cb_(_, data, size):

KeyboardInterrupt: 
^CException ignored on calling ctypes callback function: <function PerfEventArray._open_perf_buffer.<locals>.raw_cb_ at 0x7f5b7deeb2e0>
Traceback (most recent call last):
  File "/usr/lib/python3/dist-packages/bcc/table.py", line 980, in raw_cb_
    def raw_cb_(_, data, size):

KeyboardInterrupt: 
^CException ignored on calling ctypes callback function: <function PerfEventArray._open_perf_buffer.<locals>.raw_cb_ at 0x7f5b7deeaac0>
Traceback (most recent call last):
  File "/usr/lib/python3/dist-packages/bcc/table.py", line 980, in raw_cb_
    def raw_cb_(_, data, size):

KeyboardInterrupt: 
^C
Test Summary: Context Switch Latency stats: 
         min =  590 ns 
         max =  579686576 ns 
         avg =  3553156.302830308 ns 
         event count =  31516
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

#### References
Some references to this sssue:

[1] https://github.com/iovisor/bcc/pull/4074

[2] https://github.com/iovisor/bcc/issues/728


## Test code

TODO
