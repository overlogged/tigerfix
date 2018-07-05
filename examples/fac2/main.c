#include <stdio.h>
#include <unistd.h>
#include <tigerfix/def.h>

int f2(int);
int f1(int);

int f1(int n){
    if(n <= 1) return 1;
    if(n % 2) return n * f1(n - 1);
    else return n * f2(n - 1);
}

int f2(int n){
    if(n <= 1) return 1;
    if(n % 2) return n * f1(n - 1);
    else return n * f2(n - 1);
}

int main(){
    for(int i = 0; i < 100000; i ++){
        int b = f1(i);
        printf("%d\n", b);
        sleep(1);
    }
}
