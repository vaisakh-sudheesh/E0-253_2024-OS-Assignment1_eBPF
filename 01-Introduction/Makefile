
all: hello_world.bpf.o hello_world.bpf.S


# https://bugzilla.redhat.com/show_bug.cgi?id=1618958 for -O2 usage

COMMON_BPF_DEFS = -target bpf -I/usr/include/$(shell uname -m)-linux-gnu -O2


# https://blog.aquasec.com/vmlinux.h-ebpf-programs
build_vmlinux.h: 
	bpftool btf dump file /sys/kernel/btf/vmlinux  format c > vmlinux.h

hello_world.bpf.o: %.o: %.c build_vmlinux.h
	clang $(COMMON_BPF_DEFS)  -c $< -o $@ 
	llvm-objdump -D $@ > $@.S

hello_world.bpf.S: %.S: %.c build_vmlinux.h
	clang $(COMMON_BPF_DEFS) -S -c $< -o $@

### Targets to manage bpftool operation 

test-bpf-trace: unload-bpf hello_world.bpf.o
	sudo bpftool prog load hello_world.bpf.o /sys/fs/bpf/hello_world autoattach
	sudo python test-helloworld.py
	sudo rm -f /sys/fs/bpf/hello_world

load-bpf: hello_world.bpf.o
	sudo bpftool prog load hello_world.bpf.o /sys/fs/bpf/hello_world autoattach

unload-bpf:
	sudo rm  -f /sys/fs/bpf/hello_world

## Cleanup target
clean:
	rm hello_world.bpf.S hello_world.bpf.o hello_world.bpf.o.S vmlinux.h