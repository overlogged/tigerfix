#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 29 16:44:20 2018

@author: wtx
"""
import lief
#prepare
libm_main = lief.ELF.parse("../../examples/print_prime/obj/main")
libm_fix  = lief.ELF.parse("../../examples/print_prime/obj/patch.so")
head=libm_main.header
signal=str(head.file_type).split('.')[1]
if(signal=='EXECUTABLE'):
    sig=0
else:
    sig=1
#the second tab
libm_symname = [x.name for x in libm_fix.symbols]
libm_symname=set(libm_symname)
fixfunc = []
fixfunc_addr=[]
for x in libm_symname:
    if(x[:4]=='fix_'):
        fixfunc_addr.append(hex(libm_fix.get_symbol(x).value))
        fixfunc.append(x[4:])
#print(fixfunc_addr)
func_addr=[]
for y in fixfunc:
    try:
        func_addr.append(hex(libm_main.get_symbol(y).value))#str!!
        #print(libm_main.get_symbol(y))
    except:
        raise NameError("Symbols not found")
#first tab

globalname=[]
for x in libm_symname:
    if(libm_fix.get_symbol(x).value==int("c0ffee",16)):
        globalname.append(x)
globaladdr=[]
for y in globalname:
    globaladdr.append(hex(libm_main.get_symbol(y).value))
    #print(libm_main.get_symbol(y))

got_addr=[]
relocate=list(libm_fix.relocations)
for name in globalname:
    for i in range(len(globalname)):
        if relocate[i].symbol.name==name:
            got_addr.append(hex((relocate[i].address)))
#print([x for x in got_addr])
f=open('config','w+')
f.write('%d\n'%sig)
f.write("%d\n"%len(globalname))
for i in range(len(globaladdr)):
    f.write(got_addr[i]+' '+globaladdr[i]+'\n')
f.write("%d\n"%len(func_addr))
for i in range(len(func_addr)):
    f.write(func_addr[i]+' '+fixfunc_addr[i]+'\n')
f.close()