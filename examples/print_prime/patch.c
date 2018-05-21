//
// Created by nicekingwei on 18-5-21.
//

#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>
#include <tigerfix/dev.h>

extern int global_data;
extern void print_global();

PATCH_VERSION("1.0");

FIXFUN(is_prime)
int is_prime(int n) {
    print_global();
    global_data += 2;
    for (int i = 2; i * i < n; i++) {
        if (n % i == 0) return 0;
    }
    return 1;
}