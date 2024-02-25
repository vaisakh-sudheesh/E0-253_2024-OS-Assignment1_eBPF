## 4. Write a BCC program to measure the average time taken by processes in the system (context switch time =
## difference between the time when the second process starts and the first process stops).
##
## Expected Deliverable: A single file with your code that outputs min, max and mean of the context switch
## time (the output should appear when Ctrl+C is pressed after running your program).

from bcc import BPF
from bcc.utils import printb
from time import sleep

bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>


BPF_ARRAY(stats_min, u64, 1);
BPF_ARRAY(stats_max, u64, 1);
BPF_ARRAY(stats_mean, u64, 1);

BPF_ARRAY(stats_entryts, u64, 1);
BPF_ARRAY(stats_exitts, u64, 1);


int schedule_entry (struct pt_regs *ctx) {
    u64 init_z = 0;
    uint32_t zero = 0;
    u64 *ts = stats_entryts.lookup_or_init(&zero, &init_z);
    *ts = bpf_ktime_get_ns();
    bpf_trace_printk("schedule_entry++");
    return 0;
}

int schedule_ret (struct pt_regs *ctx) {
    u64 init_z = 0;
    uint32_t zero = 0;
    u64 delta = 0;
    u64 *min = stats_min.lookup_or_init(&zero, &init_z);
    u64 *max = stats_max.lookup_or_init(&zero, &init_z);
    u64 *mean = stats_mean.lookup_or_init(&zero, &init_z);
    u64 *entry_ts = stats_entryts.lookup_or_init(&zero, &init_z);
    u64 *exit_ts = stats_exitts.lookup_or_init(&zero, &init_z);

    bpf_trace_printk("schedule_ret--");
    *entry_ts = bpf_ktime_get_ns();
    
    if (*entry_ts > 0)
        delta = (*entry_ts) - (*exit_ts);
    
    *entry_ts = *exit_ts = 0;
    if (*min == 0 )
        *min = *max = delta;
    else {
        if (*min > delta)
            *min = delta;
        if (*max < delta)
            *max = delta;
    }
    return 0;
}
"""

if __name__ == '__main__':

    b = BPF(text=bpf_text)
    b.attach_kprobe(event="schedule", fn_name="schedule_entry")
    b.attach_kretprobe(event="schedule", fn_name="schedule_ret")
    print("Profiling execve... Hit Ctrl-C to end.")
    try:
        sleep(99999999)
    except KeyboardInterrupt:
        print ("Min: ", b.get_table("stats_min")[0])
        print ("Max: ", b.get_table("stats_max")[0])
        print ("Mean: ", b.get_table("stats_mean")[0])
