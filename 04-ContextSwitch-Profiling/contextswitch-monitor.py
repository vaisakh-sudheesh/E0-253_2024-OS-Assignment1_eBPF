from bcc import BPF
import collections

import sys

bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

struct sched_event_data_t{
    u64 delta;
    int active_cpu;
};

BPF_ARRAY(stats_entryts, u64);
BPF_PERF_OUTPUT(events);

int kprobe__schedule(struct pt_regs *ctx) {
    u64 init_z = 0;
    uint32_t idx = bpf_get_smp_processor_id();

    u64 *ts = stats_entryts.lookup_or_init(&idx, &init_z);
    * ts = bpf_ktime_get_ns();
    return 0;
}

int kretprobe__schedule(struct pt_regs *ctx) {
    u64 init_z = 0;
    struct sched_event_data_t evt_data;
    int cpuidx = bpf_get_smp_processor_id();

    u64 exit_ts = bpf_ktime_get_ns();
    u64 *start_ts = stats_entryts.lookup(&cpuidx);
    if (!start_ts)
        return 0;
  
    // BUG: There seems to be abnormally high delay ns values creeping through
    // ignoring them for now
    // Ref [1]: https://github.com/iovisor/bcc/pull/4074
    // Ref [2]: https://github.com/iovisor/bcc/issues/728
    if (exit_ts < *start_ts) {
        return 0;
    }

    /* Compose the event data payload and submit*/
    evt_data.active_cpu = cpuidx;
    evt_data.delta = exit_ts - *start_ts;
    events.perf_submit(ctx, &evt_data, sizeof(evt_data));
    return 0;
}
"""

sched_ctxswtch_dequeue = collections.deque()
sched_ctxswtch_evtcnt = 0
skip_processing = False

def print_schedstats():
    global sched_ctxswtch_min, sched_ctxswtch_max, sched_ctxswtch_avg, sched_ctxswtch_evtcnt
    min_val =  min(sched_ctxswtch_dequeue)
    max_val = max(sched_ctxswtch_dequeue)
    avg_val = sum(sched_ctxswtch_dequeue)/len(sched_ctxswtch_dequeue)

    print ('\nTest Summary: Context Switch Latency stats:',
            '\n\t min = ',min_val, 'ns (', (min_val/1000000),' ms)',
            '\n\t max = ',max_val , 'ns (', (max_val/1000000),' ms)'
            '\n\t avg = ', avg_val, 'ns (', (avg_val/1000000),'ms )'
            '\n\t event count = ', sched_ctxswtch_evtcnt
            )
    
def process_event(cpu, data, size):
    global skip_processing, sched_ctxswtch_evtcnt
    global b
    try:
        if (skip_processing == True):
            return
        event = b["events"].event(data)        

        # BUG: There seems to be abnormally high delay ns values creeping through
        # ignoring them for now
        # Ref [1]: https://github.com/iovisor/bcc/pull/4074
        # Ref [2]: https://github.com/iovisor/bcc/issues/728
        if (event.delta > 200000000000000):
            print("TASK/BUG: VERY HIGH value cpu %d ctx-switch-lat: %d ns\n\n" % (event.active_cpu,event.delta),)
        else:            
            sched_ctxswtch_evtcnt += 1
            sched_ctxswtch_dequeue.append(event.delta)
    except Exception:
        sys.exit(0)


if __name__ == '__main__':
    b = BPF(text=bpf_text)
    b["events"].open_perf_buffer(process_event)

    print("Profiling scheduler... Hit Ctrl-C to end.")
    while 1:
        try:
            b.perf_buffer_poll()
        except KeyboardInterrupt:
            skip_processing = True
            print_schedstats()
            exit()
    
