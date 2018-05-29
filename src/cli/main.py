import argparse
import ptrace.debugger
import subprocess
import sys
import signal
import os

def wait_stopped(pid):
    while True:
        res, status = os.waitpid(pid, 0)
        if os.WIFSTOPPED(status):
            break

def wait_trap(pid):
    while True:
        res, status = os.waitpid(pid, 0)
        if os.WIFSTOPPED(status) and os.WSTOPSIG(status) == signal.SIGTRAP:
            break

def main():
    # Argument Parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("pid", help="the process id of which process you want to hotfix", type=int)
    parser.add_argument("--cpath", help="the filepath of config file")
    args = parser.parse_args()
    pid = args.pid
    cpath = args.cpath
    
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
    # TODO: 静态链接不能拒绝
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
    # nm /usr/local/lib/libtfix.so | grep do_fix_entry
    temp_cmd = "nm /usr/local/lib/libtfix.so | grep do_fix_entry"
    temp_address = os.popen(temp_cmd).read().split(' ')[0]
    # do_fix_entry = shell_base + 0x0000000000000d30
    do_fix_entry = shell_base + int(temp_address, base=16)

    print("do_fix_entry: 0x%d", hex(do_fix_entry))

    # initialize debugger
    debugger = ptrace.debugger.PtraceDebugger()

    # attach the running process (pid)
    process = debugger.addProcess(pid, False)
    
    # next syscall
    ENOSYS = 38
    while True:
        process.syscall()
        wait_stopped(pid)
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

    # for debugging
    while False:
        process.singleStep()
        test_regs = process.getregs()
        print(test_regs.rip)

    process.cont()

    process.waitSignals(signal.SIGTRAP, signal.SIGSTOP)
    # wait_trap(pid)

    # restore old regs
    process.setregs(old_regs)

    # detach and quit
    process.detach()
    debugger.quit()
    
    
    # TODO: config file
    if False:
        try:
            config_file = open(cpath)
        except IOError as e:
            print("Couldn't open config file (%s)!" % e)


main()
