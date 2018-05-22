#include <unistd.h>
#include <sys/ptrace.h>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <fstream>
#include <string>
#include <sys/user.h>
#include <wait.h>
#include <sys/user.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/ptrace.h>
#include <assert.h>


#define MAX_BUF 4096

char buffer[MAX_BUF];

struct user_regs_struct old_regs, new_regs;

using namespace std;


void wait_stopped(pid_t pid){
    int status;
    while(true){
        assert(waitpid(pid,&status,0)!=-1);
        printf("%d\n",status);
        if(WIFSTOPPED(status)){
            break;
        }
    }
}

void wait_trap(pid_t pid){
    int status;
    while(true){
        assert(waitpid(pid,&status,0)!=-1);

        // for debug
        printf("%d %d %d %d\n",status,WIFSTOPPED(status),WSTOPSIG(status) == SIGTRAP,WSTOPSIG(status));
        struct user_regs_struct regs;
        assert(ptrace(PTRACE_GETREGS, pid, NULL, &regs)==0);

        if(WIFSTOPPED(status) && WSTOPSIG(status) == SIGTRAP){
            break;
        }
    }
}


/**
 * assert
 *  1. cat /proc/pid/maps   maxlen=4096
 *  2. cat /proc/pid/maps   first line is main
 */
int main(int argc, const char *argv[]) {

    if (argc < 2) {
        cout << "fatal error\n";
        return -1;
    }
    auto pid = (pid_t) (strtol(argv[1], nullptr, 10));

    // calc base
    uint64_t shell_base = 0, main_base = 0;

    char filename[1024];
    sprintf(filename, "/proc/%d/maps", pid);
    ifstream fmap(filename);

    bool is_first = true;
    string str_tiger = "libtfix.so";
    while (!fmap.eof()) {
        fmap.getline(buffer, MAX_BUF);
        string line(buffer);
        if (is_first) {
            auto end = line.find('-');
            auto str_base = line.substr(0, end);
            main_base = (uint64_t) strtol(str_base.c_str(), nullptr, 16);
            is_first = false;
        } else {
            auto it = line.find(str_tiger);
            if (it != string::npos) {
                auto end = line.find('-');
                auto str_base = line.substr(0, end);
                shell_base = (uint64_t) strtol(str_base.c_str(), nullptr, 16);
                break;
            }
        }
    }

    // x86-64
    auto do_fix_entry = (shell_base + 0x0000000000000960);    // nm libtfix.so | grep do_fix_entry

    int status;
    printf("do_fix_entry: 0x%lx\n",do_fix_entry);

    // attach
    assert(ptrace(PTRACE_ATTACH, pid, NULL, 0)==0);
    wait_stopped(pid);

    // next syscall
    long eax;
    do {
        assert(ptrace(PTRACE_SYSCALL, pid, NULL, NULL) == 0);
        wait_stopped(pid);
        errno = 0;
        eax = ptrace(PTRACE_PEEKUSER, pid, offsetof(struct user, regs.rax), NULL);
        assert(errno==0);
    } while (eax == -ENOSYS);


    // save status
    assert(ptrace(PTRACE_GETREGS, pid, NULL, &old_regs)==0);

    // printf("%u %llx %llx\n",pid,old_regs.rip,old_regs.rdi);

    // set reg
    new_regs = old_regs;

    new_regs.rdi = main_base;
    new_regs.rip = do_fix_entry;
    new_regs.rsp = (new_regs.rsp/32)*32;

    assert(ptrace(PTRACE_SETREGS,pid,NULL,&new_regs)==0);
    assert(ptrace(PTRACE_CONT, pid, NULL, NULL) == 0);
    wait_trap(pid);

    assert(ptrace(PTRACE_SETREGS,pid,NULL,&old_regs)==0);
    assert(ptrace(PTRACE_DETACH,pid,NULL,NULL) == 0);

    return 0;
}