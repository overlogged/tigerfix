#define _GNU_SOURCE

#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>

typedef u_int64_t ptr_t;

__asm__(
".global do_fix_entry\n\t"
"do_fix_entry:\n\t"
"callq do_fix\n\t"
"int $0x3\n\t"
);

__attribute_used__ __uint64_t tigerfix_magic = 0x20796b73;

static __attribute_noinline__ __attribute_used__ void do_fix(void *pmain) {

    if (tigerfix_magic) tigerfix_magic = 0x20796b73;

    // load
    void *handle = dlopen("./patch.so", RTLD_LAZY); // config: patch.so
    if (!handle) {
        fprintf(stderr, "%s\n", dlerror());
        exit(-1);
    }

    // init
    Dl_info so_info, main_info;
    int rc;

    // get main_info
    rc = dladdr(pmain, &main_info);
    if (!rc) {
        fprintf(stderr, "%s\n", dlerror());
        exit(-1);
    }

    const char *patch_version = dlsym(handle, "patch_version");
    rc = dladdr(patch_version, &so_info);
    if (!patch_version || !rc) {
        fprintf(stderr, "%s\n", dlerror());
        exit(-1);
    }

    const long pagesize = sysconf(_SC_PAGE_SIZE);

    // redirect symbols in so
    ptr_t *ext_symbols = malloc(sizeof(ptr_t) * 4); // config: external symbols
    ptr_t *fix_units = malloc(sizeof(ptr_t) * 2);   // config: fix units

    ext_symbols[0] = (ptr_t) 0x0000000000200ff8;    // objdump -R patch.so | grep global_data
    ext_symbols[1] = (ptr_t) 0x000000000020101c;    // nm main | grep global_data
    ext_symbols[2] = (ptr_t) 0x0000000000201018;    // objdump -R patch.so | grep print_global
    ext_symbols[3] = (ptr_t) 0x00000000000007f0;    // nm main | grep print_global
    fix_units[0] = (ptr_t) 0x0000000000000810;      // nm main | grep is_prime
    fix_units[1] = (ptr_t) 0x0000000000000340;      // nm patch.so | grep fix_is_prime

    ptr_t so_base = (ptr_t) so_info.dli_fbase;
    ptr_t main_base = (ptr_t) main_info.dli_fbase;

    // fix got
    for (int i = 0; i < 2; i++) {
        ptr_t *p_got_item = (ptr_t *) (ext_symbols[2 * i] + so_base);
        ptr_t real_addr = ext_symbols[2 * i + 1] + main_base;

        void *pg = (void *) ((ptr_t) p_got_item & ~(pagesize - 1));
        mprotect(pg, pagesize, PROT_READ | PROT_WRITE | PROT_EXEC);

        *p_got_item = real_addr;
    }

    // fix
    for (int i = 0; i < 1; i++) {

        ptr_t old_func = main_base + fix_units[2 * i];
        ptr_t new_func = so_base + fix_units[2 * i + 1];


        void *pg = (void *) (old_func & ~(pagesize - 1));
        mprotect(pg, pagesize, PROT_READ | PROT_WRITE | PROT_EXEC);

        // modify entry
        u_int8_t *old_entry = (u_int8_t *) old_func;

        // push %rax
        old_entry[0] = 0x50;

        // movq %0xc0ffee,%%rax
        old_entry[1] = 0x48;
        old_entry[2] = 0xb8;
        *((ptr_t *) (old_func + 3)) = new_func;

        // jmpq *%rax
        old_entry[11] = 0xff;
        old_entry[12] = 0xe0;

        // nop
        old_entry[13] = old_entry[14] = old_entry[15] = 0x90;

        mprotect(pg, pagesize, PROT_READ | PROT_EXEC);
        // todo: 2 pages
    }
}