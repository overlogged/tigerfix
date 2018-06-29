import ptrace.debugger
import subprocess
import sys
import signal
import os
import lief
from . import root

def wait_stopped(pid):
    while True:
        _, status = os.waitpid(pid, 0)
        if os.WIFSTOPPED(status):
            break

def wait_trap(pid):
    while True:
        _, status = os.waitpid(pid, 0)
        if os.WIFSTOPPED(status) and os.WSTOPSIG(status) == signal.SIGTRAP:
            break

def main(args):
    root.get_root()

    # Get parameters from args
    pid = args.pid

    # Calculating base address
    shell_base = 0
    main_base = 0
    proc_map_filename = "/proc/%d/maps" % pid

    try:
        fmap = open(proc_map_filename)
    except IOError as e:
        print("Couldn't open process map file (%s)!" % e)

    try:
        lines = fmap.readlines()
    except e:
        print(e)
        exit(-1)

    is_first = True
    str_tiger = "libtfix.so"
    # TODO: 无链接则拒绝
    for line in lines:
        if is_first:
            end = line.find('-')
            str_base = line[0:end]
            main_base = int(str_base, base=16)
            is_first = False
        else:
            it = line.find(str_tiger)
            if (it != -1):
                end = line.find('-')
                str_base = line[0:end]
                shell_base = int(str_base, base=16)
                break
    
    # x86-64
    # nm /usr/lib/libtfix.so | grep do_fix_entry
    
    libm_tfix=lief.ELF.parse("/usr/lib/libtfix.so")
    symbol_name=[x.name for x in libm_tfix.symbols]

    if "do_fix_entry" in symbol_name:
        tfix=libm_tfix.get_symbol("do_fix_entry")
        temp_address = int(tfix.value)
    else:
        raise NameError("do_fix_entry not found")
    
    do_fix_entry = shell_base + temp_address

    # initialize debugger
    debugger = ptrace.debugger.PtraceDebugger()

    # attach the running process (pid)
    process = debugger.addProcess(pid, False)
    
    # next syscall
    ENOSYS = 38
    while True:
        process.syscall()
        wait_stopped(pid)
        # process.waitSignals(signal.SIGSTOP)
        eax = process.getreg('eax')
        if eax != -ENOSYS:              # if not invalid syscall
            break

    # save status
    old_regs = process.getregs()

    # set regs
    new_regs = process.getregs()

    # 32 bit && 64 bit
    new_regs.rdi = main_base
    new_regs.rip = do_fix_entry
    new_regs.rsp = int((new_regs.rsp / 32)) * 32

    # set new regs
    process.setregs(new_regs)

    process.cont()

    # process.waitSignals(signal.SIGTRAP, signal.SIGSTOP)
    wait_trap(pid)

    # restore old regs
    process.setregs(old_regs)

    # detach and quit
    process.detach()
    debugger.quit()

# if __name__ == '__main__':
#     main()