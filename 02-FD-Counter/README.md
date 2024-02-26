# BPFTrace: Count open file descritors

## Question
Develop a bpftrace script to show the number of files currently opened (it should be equal to file descriptors held by process under /proc directory) by a particular process.

**Expected Deliverable:** Mostly a single-line program. Must have standard sections present in bpftrace script. Learn more about each section of the single-line script.


## Solution

Command invocation invocation
```bash
sudo ./FD-counter-pid.bt <pid>
```

Example invocation:
```bash
vaisakh@VPS-TW:[02-FD-Counter]> sudo ./FD-counter-pid.bt 472451
Attaching 1 probe...


@fdcount: 1
```

| :warning: WARNING           |
|:----------------------------|
| Sometimes, the number of file descriptors can change between manual or automated sampling of ```/proc/<pid>/fdinfo``` path and bpftrace invocation, so there can be mismatch in numbers obtained in few cases.    |

## Test code

A test code to iterate through the ```/proc/<pid>``` entries is added to count file descriptor in ```fdinfo``` and invoke bpftrace script too and validate input

```bash
vaisakh@VPS-TW:[02-FD-Counter]> sudo python3 testcode.py
```
