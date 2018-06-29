#define _GNU_SOURCE

#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>
#include <string.h>
#include <assert.h>

#ifdef __i386__

#include <stddef.h>
#define RIP(R) (R).eip
#define RAX(R) (R).eax
#define RDI(R) (R).edi
#define RSP(R) (R).esp
#define REGS_RAX regs.eax
#define ADDRTYPE "%x"
typedef u_int32_t addr_t;

#elif defined(__x86_64__)

#define RIP(R) (R).rip
#define RAX(R) (R).rax
#define RDI(R) (R).rdi
#define RSP(R) (R).rsp
#define REGS_RAX regs.rax
#define ADDRTYPE "%lx"
typedef u_int64_t addr_t;

#else

#error Unsupported architecture

#endif

typedef addr_t ptr_t;


#ifdef __i386__
addr_t uesp;
__asm__(
".global do_fix_entry\n\t"
"do_fix_entry:\n\t"
"mov %esp,uesp\n\t"
"call do_fix\n\t"
"int $0x3\n\t"
);
#elif defined(__x86_64__)
__asm__(
".global do_fix_entry\n\t"
"do_fix_entry:\n\t"
//"mov %rsp,uesp\n\t"
"callq do_fix\n\t"
"int $0x3\n\t"
);
#endif


__attribute_used__ __uint64_t tigerfix_magic = 0x20796b73;

char soname[4096];

#ifdef __i386__
static __attribute_noinline__ __attribute_used__ void do_fix() {
#elif defined(__x86_64__)
static __attribute_noinline__ __attribute_used__ void do_fix(void *uesp) {
#endif
    const char *path = (char *)uesp;
    // puts(path);

    addr_t pmain = strtol(path + 4032, NULL, 10);
    // printf("pmain: "ADDRTYPE"\n", pmain);

    if (tigerfix_magic) tigerfix_magic = 0x20796b73;

    // read config
    FILE *fp = fopen(path, "rb");
    assert(fp != NULL);
    int flag, n, m;
	addr_t (*sym)[2], (*addr)[2];

	assert(fscanf(fp, "%d%d", &flag, &n) != EOF);

	sym = (addr_t(*)[2])malloc(sizeof(addr_t) * 2 * n);
	for(int i = 0; i < n; i ++){
		assert(fscanf(fp, ADDRTYPE""ADDRTYPE, &sym[i][0], &sym[i][1]) != EOF);
	}

	assert(fscanf(fp, "%d", &m) != EOF);

    addr = (addr_t(*)[2])malloc(sizeof(addr_t) * 2 * m);
	for(int i = 0; i < m; i ++) {
		assert(fscanf(fp, ADDRTYPE""ADDRTYPE, &addr[i][0], &addr[i][1]) != EOF);
	}

	// read and generate patch.tfp.so
	// assert: elf start with 0x7f and there is no 0x7f between config and elf
	while(fgetc(fp) != 0x7f);
	fseek(fp, -1L, SEEK_CUR);

	long start = ftell(fp);
	fseek(fp, 0L, SEEK_END);
	long end = ftell(fp);
	fseek(fp, start, SEEK_SET);
	size_t len = end - start;

	void *mem = malloc(sizeof(char) * len);
	assert(fread(mem, len, 1, fp) == 1);
	strcpy(soname, path);
    size_t slen = strlen(soname);
    soname[slen++] = '.';
    soname[slen++] = 's';
    soname[slen++] = 'o';
    soname[slen++] = '\0';

	FILE *fpso = fopen(soname, "wb");
    assert(fpso != NULL);
	assert(fwrite(mem, len, 1, fpso) == 1);
	fclose(fpso);
	fclose(fp);

    // load
    void *handle = dlopen(soname, RTLD_LAZY);
    if (!handle) {
        fprintf(stderr, "%s\n", dlerror());
        exit(-1);
    }

    // init
    Dl_info so_info, main_info;
    int rc;

    // get main_info
    rc = dladdr((const void *)pmain, &main_info);
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
    ptr_t *ext_symbols = malloc(sizeof(ptr_t) * 2 * n);
    ptr_t *fix_units = malloc(sizeof(ptr_t) * 2 * m);

    for(int i = 0; i < n; i ++){
		ext_symbols[2 * i] = sym[i][0];
		ext_symbols[2 * i + 1] = sym[i][1];
    }
    for(int i = 0; i < m; i ++){
		fix_units[2 * i] = addr[i][0];
		fix_units[2 * i + 1] = addr[i][1];
    }

    /*
     objdump -R patch.so | grep global_data && nm main | grep global_data && objdump -R patch.so | grep print_global && nm main | grep print_global && nm main | grep is_prime && nm patch.so | grep fix_is_prime
    */
    ptr_t so_base = (ptr_t) so_info.dli_fbase;
    ptr_t main_base = (ptr_t) main_info.dli_fbase * flag;	// flag:  0 for abs

    // fix got
    for (int i = 0; i < 2; i++) {
        ptr_t *p_got_item = (ptr_t *) (ext_symbols[2 * i] + so_base);
        ptr_t real_addr = ext_symbols[2 * i + 1] + main_base;

        void *pg = (void *) ((ptr_t) p_got_item & ~(pagesize - 1));
        mprotect(pg, pagesize, PROT_READ | PROT_WRITE | PROT_EXEC);

        *p_got_item = real_addr;

		mprotect(pg, pagesize, PROT_READ | PROT_EXEC);
    }

    // fix
    for (int i = 0; i < 1; i++) {

        ptr_t old_func = main_base + fix_units[2 * i];
        ptr_t new_func = so_base + fix_units[2 * i + 1];

        void *pg1 = (void *) (old_func & ~(pagesize - 1));
        void *pg2 = (void *) ((old_func + 16) & ~(pagesize - 1));

        mprotect(pg1, pagesize, PROT_READ | PROT_WRITE | PROT_EXEC);
        if(pg2 != pg1) mprotect(pg2, pagesize, PROT_READ | PROT_WRITE | PROT_EXEC);

        // modify entry
        u_int8_t *old_entry = (u_int8_t *) old_func;

#ifdef __i386__

        // jmp new_func
        old_entry[0] = 0xe9;
        *((ptr_t *) (old_entry + 1)) = (char *)new_func - (char *)old_entry - 5;

        // nop
        //old_entry[5] = old_entry[6] = old_entry[7] = 0x90;


#elif defined(__x86_64__)

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

#endif

        mprotect(pg1, pagesize, PROT_READ | PROT_EXEC);
        if(pg1 != pg2) mprotect(pg2, pagesize, PROT_READ | PROT_EXEC);

    }
	free(sym);
	free(addr);
	free(ext_symbols);
	free(fix_units);
	free(mem);
	// printf("fix finish\n");
}
