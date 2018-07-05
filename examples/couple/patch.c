#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>
#include <tigerfix/dev.h>

extern int f2(int);

PATCH_VERSION("1.0");

FIXFUN(f1)
int f1(int n) {
   return f2(2);
}
