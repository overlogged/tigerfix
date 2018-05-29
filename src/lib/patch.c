#define _GNU_SOURCE

#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>
#include <string.h>

typedef u_int64_t ptr_t;

__asm__(
".global do_fix_entry\n\t"
"do_fix_entry:\n\t"
"callq do_fix\n\t"
"int $0x3\n\t"
);

__attribute_used__ __uint64_t tigerfix_magic = 0x20796b73;


static __attribute_noinline__ __attribute_used__ void do_fix(void *pmain) {

	const char *path = "/home/yxy/桌面/hotfixwork5.6/test/tigerfix/src/cli/configandpatch.tfp";

    if (tigerfix_magic) tigerfix_magic = 0x20796b73;

    //read config
    FILE *fp = fopen(path, "rb");
    if(!fp) {
		fprintf(stderr, "cannot open tfix.config!\n");
		exit(-1);
    }
    int flag, n, m;
	u_int64_t (*sym)[2], (*addr)[2];

	if(EOF == fscanf(fp, "%d%d", &flag, &n)) exit(-1);
	sym = (u_int64_t(*)[2])malloc(sizeof(u_int64_t) * 2 * n);
	for(int i = 0; i < n; i ++){
		if(EOF == fscanf(fp, "%lx%lx", &sym[i][0], &sym[i][1])) exit(-1);
	}
	if(EOF == fscanf(fp, "%d", &m)) exit(-1);
	addr = (u_int64_t(*)[2])malloc(sizeof(u_int64_t) * 2 * m);
	for(int i = 0; i < m; i ++){
		if(EOF == fscanf(fp, "%lx%lx", &addr[i][0], &addr[i][1])) exit(-1);
	}

	//read elf
	if(fgetc(fp) != '\n') exit(-1);		//要保证tfp文件的config最后一个字符是单一的\n 之后紧接着patch
	long start = ftell(fp);
	fseek(fp, 0L, SEEK_END);
	long end = ftell(fp);
	fseek(fp, start, SEEK_SET);
	size_t len = end - start;
	void *mem = malloc(sizeof(char) * len);
	if(1 != fread(mem, len, 1, fp)) exit(-1);
	char soname[4096];
	strcpy(soname, path);
	strcat(soname, ".so");
	FILE *fpso = fopen(soname, "wb");
	if(!fpso) exit(-1);
	if(1 != fwrite(mem, len, 1, fpso)) exit(-1);
	fclose(fpso);
	fclose(fp);

	//test read result
//	fprintf(stdout, "\n%d\n%d\n", flag, n);
//	for(int i = 0; i < n; i ++){
//		fprintf(stdout, "%0lx %0lx\n", sym[i][0], sym[i][1]);
//	}
//	fprintf(fp, "%d\n", m);
//	for(int i = 0; i < m; i ++){
//		fprintf(stdout, "%0lx %0lx\n", addr[i][0], addr[i][1]);
//	}
//

/*
diff /home/yxy/桌面/hotfixwork5.6/test/tigerfix/src/cli/configandpatch.tfp.so /home/yxy/桌面/hotfixwork5.6/test/tigerfix/examples/print_prime/obj/patch.so
*/

    // load
    void *handle = dlopen(soname, RTLD_LAZY); // config: patch.so  soname
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
    ptr_t *ext_symbols = malloc(sizeof(ptr_t) * 2 * n); // config: external symbols
    ptr_t *fix_units = malloc(sizeof(ptr_t) * 2 * m);   // config: fix units

    for(int i = 0; i < n; i ++){
		ext_symbols[2 * i] = sym[i][0];
		ext_symbols[2 * i + 1] = sym[i][1];
    }
    for(int i = 0; i < m; i ++){
		fix_units[2 * i] = addr[i][0];
		fix_units[2 * i + 1] = addr[i][1];
    }
//
//    ext_symbols[0] = (ptr_t) 0x00000000002005d0;    // objdump -R patch.so | grep global_data
//    ext_symbols[1] = (ptr_t) 0x000000000020104c;    // nm main | grep global_data
//    ext_symbols[2] = (ptr_t) 0x00000000002005c8;    // objdump -R patch.so | grep print_global
//    ext_symbols[3] = (ptr_t) 0x00000000000007a0;    // nm main | grep print_global
//    fix_units[0] = (ptr_t) 0x0000000000000720;      // nm main | grep is_prime
//    fix_units[1] = (ptr_t) 0x0000000000000370;      // nm patch.so | grep fix_is_prime
/*
objdump -R patch.so | grep global_data && nm main | grep global_data && objdump -R patch.so | grep print_global && nm main | grep print_global && nm main | grep is_prime && nm patch.so | grep fix_is_prime
*/
    ptr_t so_base = (ptr_t) so_info.dli_fbase;
    ptr_t main_base = (ptr_t) main_info.dli_fbase * flag;	//flag = 绝对地址  flag = 相对地址

    printf("new func addr should be %p\n", dlsym(handle, "fix_is_prime"));

    // fix got
    for (int i = 0; i < 2; i++) {
        ptr_t *p_got_item = (ptr_t *) (ext_symbols[2 * i] + so_base);
        ptr_t real_addr = ext_symbols[2 * i + 1] + main_base;

		printf("got is %p -- realaddr is %lx\n", p_got_item, real_addr);

        void *pg = (void *) ((ptr_t) p_got_item & ~(pagesize - 1));
        mprotect(pg, pagesize, PROT_READ | PROT_WRITE | PROT_EXEC);
        mprotect(pg + pagesize, pagesize, PROT_READ | PROT_WRITE | PROT_EXEC);

        *p_got_item = real_addr;

		mprotect(pg, pagesize, PROT_READ | PROT_EXEC);
        mprotect(pg + pagesize, pagesize, PROT_READ | PROT_EXEC);
    }

    // fix
    for (int i = 0; i < 1; i++) {

        ptr_t old_func = main_base + fix_units[2 * i];
        ptr_t new_func = so_base + fix_units[2 * i + 1];

        printf("oldfuncaddr is %lx -- newfuncaddr is %lx\n", old_func, new_func);

        void *pg = (void *) (old_func & ~(pagesize - 1));
        mprotect(pg, pagesize, PROT_READ | PROT_WRITE | PROT_EXEC);
        mprotect(pg + pagesize, pagesize, PROT_READ | PROT_WRITE | PROT_EXEC);

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
        mprotect(pg + pagesize, pagesize, PROT_READ | PROT_EXEC);

    }

	free(sym);
	free(addr);
	free(ext_symbols);
	free(fix_units);
	free(mem);
}
