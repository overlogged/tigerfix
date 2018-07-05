#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>
#include <tigerfix/dev.h>


PATCH_VERSION("1.0");

FIXFUN(factorial) 
int factorial(int n)
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
		result = factorial(n - 2) * n;//改为！！
	}
	return result;
}
