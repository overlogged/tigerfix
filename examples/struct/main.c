#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <tigerfix/def.h>

struct student{
    char name[16];
    char prefix[3];
    int id;
};

struct student input_student_info(char* name, char* prefix, int id){
    struct student a;
    strcpy(a.name, name);
    strcpy(a.prefix, prefix);
    a.id = id;
    return a;
}

void print_student_name(struct student a){
    printf("Student's name is: %s\n", a.name);
}

void print_student_id(struct student a){
    printf("Student's id is: %s%d\n", a.prefix, a.id);
}

void print_student(struct student a){
    print_student_name(a);
    print_student_id(a);
}

__attribute_noinline__ void event_loop(const char* name){
    struct student ljw = input_student_info("longjinwei", "JL", 17110067);
    if(strcmp(name,"ljw")==0){
        print_student(ljw);
    }else{
        printf("no such student.\n");
    }
}

int main(){
    while(1){
        event_loop("ljw");
        sleep(10);
    }
    return 0;
}