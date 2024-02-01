#include "vmlinux.h"
#include <bpf/bpf_helpers.h>

SEC("tracepoint/syscalls/sys_enter_execve")
int tracepoint_syscalls_sys_enter_execve(struct trace_event_raw_sys_enter *ctx) {
    bpf_printk("Hello Worldddd!!!\n");
    return 0;
}

char LICENSE[] SEC("license") = "Dual BSD/GPL";
