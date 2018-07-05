#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/mman.h>
#include <tigerfix/dev.h>

struct student{
    char name[16];
    char prefix[3];
    int id;
    double grade;
};

PATCH_VERSION("1.0");

FIXFUN(input_student_info)
struct student input_student_info(char* name, char* prefix, int id, double grade){
    struct student a;
    strcpy(a.name, name);
    strcpy(a.prefix, prefix);
    a.id = id;
    a.grade = grade;
    return a;
}

void print_student_name(struct student a){
    printf("Student's name is: %s\n", a.name);
}

void print_student_id(struct student a){
    printf("Student's id is: %s%d\n", a.prefix, a.id);
}


FIXFUN(print_student)
void print_student(struct student a){
    print_student_name(a);
    print_student_id(a);
    printf("%.2lf\n", a.grade);
}


FIXFUN(event_loop)
void event_loop(const char* name){
    struct student ljw = input_student_info("longjinwei", "JL", 17110067,4.3);
    if(strcmp(name,"ljw")==0){
        print_student(ljw);
    }else{
        printf("no such student.\n");
    }
}