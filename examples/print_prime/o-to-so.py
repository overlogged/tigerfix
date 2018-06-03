#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  2 17:26:34 2018

@author: wtx
"""
import lief,os
libm_patch=lief.ELF.parse("../tigerfix/examples/print_prime/obj/patch.o")
relocate_list=list(libm_patch.relocations)
symbol_list = [x.symbol.name for x in relocate_list if x.symbol.name!='']
command=''
for obj in symbol_list:
 command+=" --defsym "+obj+"=0xc0ffee"
os.system("ld obj/patch.o -shared -fno-plt"+command+" -o obj/patch.so")


