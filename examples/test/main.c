#include <stdio.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <tigerfix/def.h>

__attribute_noinline__ int p(){
	return 1;
}

void fac(){
	int i,n;
	for(i=1;i<100000;i++)
	{sleep(1);
	n = p();
	printf("%d\n",n);
	}
} 



int main() {                                         
	fac();
	return 0;
}
