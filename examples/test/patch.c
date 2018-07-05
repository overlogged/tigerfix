#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>
#include <tigerfix/dev.h>

PATCH_VERSION("1.0");

FIXFUN(p)
int p() {
    return 2;
}
