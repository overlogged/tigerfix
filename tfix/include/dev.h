//
// Created by nicekingwei on 18-5-21.
//

#ifndef TIGERFIX_DEV_H
#define TIGERFIX_DEV_H

#define FIXFUN(name) \
__asm__(\
".global fix_"#name"\n"\
"fix_"#name":\n"\
"pop %rax\n\t"\
"jmp "#name"\n\t"\
);\
static __attribute__ ((noinline,used))

#define PATCH_VERSION(v) char patch_version[] = (v);

#endif //TIGERFIX_DEV_H
