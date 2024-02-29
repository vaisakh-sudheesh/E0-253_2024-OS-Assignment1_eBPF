# BPFTrace: Count open file descritors

## Question
Develop a bpftrace script to show the number of files currently opened (it should be equal to file descriptors held by process under /proc directory) by a particular process.

**Expected Deliverable:** Mostly a single-line program. Must have standard sections present in bpftrace script. Learn more about each section of the single-line script.

## Solution Approach

Make use of **iter:task_file** bpf iterator to dump file descriptors associated with PID.

### Refernces:
- https://docs.kernel.org/bpf/bpf_iterators.html
- https://developers.facebook.com/blog/post/2022/03/31/bpf-iterator-retrieving-kernel-data-with-flexibility-and-efficiency/
- https://lwn.net/Articles/926041/
- https://github.com/bpftrace/bpftrace/blob/master/man/adoc/bpftrace.adoc#probes-iterator


> [!IMPORTANT]
> BPF Iterator functionality seems to be not working in bpftrace installed from APT. It is recommended to build and install BPF Trace from github repo


## Testing Command

Command invocation invocation
```shellscript
$ sudo ./FD-counter-pid.bt <pid>
```

Example invocation:
```shellscript
$ sudo ./FD-counter-pid.bt 472451
Attaching 1 probe...


@fdcount: 1
```

> [!IMPORTANT]
> Sometimes, the number of file descriptors can change between manual or automated sampling of ```/proc/<pid>/fdinfo``` path and bpftrace invocation, so there can be mismatch in numbers obtained in few cases.

## Test code

A test code to iterate through the ```/proc/<pid>``` entries is added to count file descriptor in ```fdinfo``` and invoke bpftrace script too and validate input

```shellscript
$ sudo python3 testcode.py
```
