# Anonymous Memory Monitoring

## Question

Write an eBPF program to compute the amount of anonymous memory used by a given program. 

> [!IMPORTANT]
> Assume huge pages are disabled for this task.

**Test case:** The test case has been uploaded in the class Teams.
**Expected Deliverable:** A single code file that outputs the anonymous memory usage of given program.

## Solution Approach

After touching the pages allocated through mmap function, as it has no physical pages mapped, a page fault will be trigered during the touch operation. This can be utilized to track anonymous memory regions.

To do so, **kfunc:vmlinux:do_anonymous_page** is used in bpftrace script.

> [!NOTE]
> In experiments it was observed that without even the mmap invocation from test code, a small region of anoymous memory is allocated in the order of *52kB* (mmap private allocation with a split up of 12.0kB clean and 40.0kB dirtry). 
> This implies that, the libc used by Linux Distro and compiler(clang in this case) has a static allocation happening for anonymous memory region.
> Interestingly, for this allocation, a pagefault is not observed or intercepted by eBPF.

Due to this reason, this factor of 52kB untracked allocation is added along in the memory calculation in code.

> [!CAUTION]
> When changing runtime (libc or compiler) or the Linux Distribution on which testing is performed, it is likely that this observed number of 52kB may vary as the libc variant and supporting code may differ. Hence for porting of this code, this factor need to be accounted for.

> [!IMPORTANT]
> The BPFTrace script accept the comm name for program to be tracked. 
>
> The shortcoming of this implementation is that, it cannot compute existing allocation on an already running program - as a limitation of this approach.
> Hence the bpftrace need to be started prior to starting test case.
> 
> Example of invocation is shown in next section.

## Testing Command

Command for starting bpftrace
```shellscript
$sudo bpftrace experiment.bt <testcase-executable>
```

Command for running testcase
```shellscript
$ make 
$ ./testcase.out
```

### Sample output

#### bpftrace execution
```shellscript
$ sudo bpftrace anon-mem-compute.bt testcase.out 
Attaching 3 probes...
Tracing anonymous allocations calls for 'testcase.out' - Hit Ctrl-C to end 
ANON MEM: page_alloc_count: 20014 (80108 kB)
ANON MEM: page_alloc_count: 20270 (81132 kB)
ANON MEM: page_alloc_count: 20526 (82156 kB)
ANON MEM: page_alloc_count: 20782 (83180 kB)
ANON MEM: page_alloc_count: 21038 (84204 kB)
ANON MEM: page_alloc_count: 21294 (85228 kB)
ANON MEM: page_alloc_count: 21550 (86252 kB)
```

#### testcase execution

```shellscript
$ ./testcase.out 
The tracing script should output following value when run parallelly:
pid: 685275 anonymous memory usage: 80108 KB
pid: 685275 anonymous memory usage: 81132 KB
pid: 685275 anonymous memory usage: 82156 KB
pid: 685275 anonymous memory usage: 83180 KB
pid: 685275 anonymous memory usage: 84204 KB
pid: 685275 anonymous memory usage: 85228 KB
pid: 685275 anonymous memory usage: 86252 KB
```
