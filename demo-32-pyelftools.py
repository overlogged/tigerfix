#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  3 22:35:49 2018

@author: wtx
"""

import elftools.elf.elffile as ef
a=open("../tigerfix/examples/print_prime/obj/patch.so",'rb')
b=open("../tigerfix/examples/print_prime/obj/main",'rb')
#prepare
elffile_patch = ef.ELFFile(a)
elffile_main = ef.ELFFile(b)

reladyn_name = '.rela.dyn'
sym_name = '.symtab'
relaplt_name = '.rela.plt'
dynsym = '.dynsym'

reladyn_patch = elffile_patch.get_section_by_name(reladyn_name)
symtab_patch = elffile_patch.get_section_by_name(sym_name)
relaplt_patch = elffile_patch.get_section_by_name(relaplt_name)
dynsym_patch = elffile_patch.get_section_by_name(dynsym)

symtab_main = elffile_main.get_section_by_name(sym_name)

#first tab
extern_name = []
main_exaddr = []
got = []#(name ,addr)
for sym in symtab_patch.iter_symbols():
    if(sym.entry['st_value']==int('c0ffee',16)):
        extern_name.append(sym.name)
for name in extern_name:
    main_exaddr.append(symtab_main.get_symbol_by_name(name)[0].entry['st_value'])


for reloc in reladyn_patch.iter_relocations():
            # Relocation entry attributes are available through item lookup
            addr = reloc['r_offset']
            name = dynsym_patch.get_symbol(reloc['r_info_sym']).name
            got.append((name, addr))
for reloc in relaplt_patch.iter_relocations():
            # Relocation entry attributes are available through item lookup
            addr = reloc['r_offset']
            name = dynsym_patch.get_symbol(reloc['r_info_sym']).name
            got.append((name, addr))
got_addr=[]
for name in extern_name:
    for name_got,addr_got in got:
        if(name_got==name):
            got_addr.append(addr_got)

#second tab
oldfunc_name=[]
patchfunc_addr=[]
mainfunc_addr=[]
for func in symtab_patch.iter_symbols():
    if(func.name[:4]=='fix_'):
        oldfunc_name.append(func.name[4:])
        patchfunc_addr.append(func.entry['st_value'])
for name in oldfunc_name:
    mainfunc_addr.append(symtab_main.get_symbol_by_name(name)[0].entry['st_value'])
    
#file type
if(elffile_main.header['e_type']=='ET_EXEC'):
    sig=0
else:
    sig=1
    
#write
f=open('config','w+')
f.write('%d\n'%sig)
f.write("%d\n"%len(extern_name))
for i in range(len(main_exaddr)):
    f.write(hex(got_addr[i])[2:]+' '+hex(main_exaddr[i])[2:]+'\n')
f.write("%d\n"%len(patchfunc_addr))
for i in range(len(patchfunc_addr)):
    f.write(hex(mainfunc_addr[i])[2:]+' '+hex(patchfunc_addr[i])[2:]+'\n')
f.close()