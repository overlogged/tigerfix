#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <tigerfix/def.h>


__attribute_noinline__ int factorial(int n)
{
	int result;
	if (n<0)                                         
	{
		printf("输入错误!\n");
		return 0;
	}
	else if (n == 0 || n == 1)
	{
		result = 1;  
	}
	else
	{
		result = factorial(n - 1) * n;
	}
	return result;
}

void fac(){
	int i,n;
	for(i=1;i<100000;i++)
	{
		sleep(10);
		n=factorial(i);
		printf("%d\n",n);
	}
} 



int main() {                                         
	fac();
	return 0;
}
