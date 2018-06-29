//
// Created by nicekingwei on 18-5-21.
//

#ifndef TIGERFIX_DEV_H
#define TIGERFIX_DEV_H


#ifdef __i386__

#define FIXFUN(name) \
__asm__(\
".global fix_"#name"\n"\
"fix_"#name":\n"\
"jmp "#name"\n\t"\
);\
static __attribute__ ((noinline,used))

#elif defined(__x86_64__)

#define FIXFUN(name) \
__asm__(\
".global fix_"#name"\n"\
"fix_"#name":\n"\
"pop %rax\n\t"\
"jmp "#name"\n\t"\
);\
static __attribute__ ((noinline,used))

#endif

#define PATCH_VERSION(v) char patch_version[] = (v);

#endif //TIGERFIX_DEV_H
