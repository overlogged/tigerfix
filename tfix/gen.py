import os
import argparse
from shutil import rmtree
import elftools.elf.elffile as elf
import elftools.elf.relocation as relocation


def hex_64bit(some_int):
    ans = format(some_int, "x")
    ans = ans.zfill(16) # 64 bit is 16 digits long in hex
    return ans

def unresolved_sym(name):
    if name=='':
        return False
    if name.find("@") != -1:
        return False
    if len(name)>=1 and (name[0]=='.' or name[0]=='_'):
        return False
    return True


def do_link(obj_files,target_file,tmp_file):
    command = "gcc %s -shared -fno-plt -o %s" % (' '.join(obj_files),tmp_file)
    # print(command)
    os.system(command)

    symbol_list = []
    nm_out = os.popen("nm -u %s" % tmp_file)
    lines = nm_out.readlines()

    nouse_symbol = []
    for line in lines:
        ss = line.split()
        if(len(ss)>0):
            sym = ss[-1]
            if(unresolved_sym(sym)):
                symbol_list.append("--defsym %s=0xc0ffee"%sym)

    command = "ld %s -lc -shared -fno-plt %s -o %s" % (' '.join(obj_files),' '.join(symbol_list),target_file)
    # print(command)
    os.system(command)
    return target_file

def main(args):

    # get parameters from args
    main_path = args.main
    patch_path = args.patch
    target_path = args.object

    if (main_path is None) or (target_path is None):
        raise AttributeError

    # create directory for the config and the tiger fix patch
    fix_dir = os.path.join(os.path.dirname(target_path),"tigerfix")
    if not os.path.isdir(fix_dir):
        os.mkdir(fix_dir)

    config_path = os.path.join(fix_dir, "config")
    so_path = os.path.join(fix_dir, "patch.so")
    tmp_file = os.path.join(fix_dir,'tmp.so')

    # link objects
    do_link(patch_path,so_path,tmp_file)

    # generating config file
    a = open(so_path,'rb')
    b = open(main_path,'rb')

    # prepare
    elffile_patch = elf.ELFFile(a)
    elffile_main = elf.ELFFile(b)
    
    if elffile_patch.elfclass==64:
        reladyn_name = '.rela.dyn'
        sym_name = '.symtab'
        relaplt_name = '.rela.plt'
        dynsym = '.dynsym'

    if elffile_patch.elfclass==32:
        reladyn_name = '.rel.dyn'
        sym_name = '.symtab'
        relaplt_name = '.rel.plt'
        dynsym = '.dynsym'

    reladyn_patch = elffile_patch.get_section_by_name(reladyn_name)
    symtab_patch = elffile_patch.get_section_by_name(sym_name)
    relaplt_patch = elffile_patch.get_section_by_name(relaplt_name)
    dynsym_patch = elffile_patch.get_section_by_name(dynsym)

    symtab_main = elffile_main.get_section_by_name(sym_name)

    # first tab
    extern_name = []
    main_exaddr = []
    got = [] #(name ,addr)
    for sym in symtab_patch.iter_symbols():
        if(sym.entry['st_value']==int('c0ffee',16)):
            extern_name.append(sym.name)
    for name in extern_name:
        main_exaddr.append(symtab_main.get_symbol_by_name(name)[0].entry['st_value'])

    if(reladyn_patch is None):
        pass
    else:
        for reloc in reladyn_patch.iter_relocations():
            # Relocation entry attributes are available through item lookup
            addr = reloc['r_offset']
            name = dynsym_patch.get_symbol(reloc['r_info_sym']).name
            got.append((name, addr))
    if(relaplt_patch is None):
        pass
    else:
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
    configfile = open(config_path,'w+')
    configfile.write('%d\n'%sig)
    configfile.write("%d\n"%len(extern_name))
    # print(extern_name)

    for i in range(len(main_exaddr)):
        configfile.write(hex(got_addr[i])[2:]+' '+hex(main_exaddr[i])[2:]+'\n')
        # print(hex(got_addr[i])[2:]+' '+hex(main_exaddr[i])[2:]+'\n')
    configfile.write("%d\n"%len(patchfunc_addr))
    for i in range(len(patchfunc_addr)):
        configfile.write(hex(mainfunc_addr[i])[2:]+' '+hex(patchfunc_addr[i])[2:]+'\n')
        # print(hex(mainfunc_addr[i])[2:]+' '+hex(patchfunc_addr[i])[2:]+'\n')
    configfile.close()


    # concat
    cfg_bin = open(config_path, 'rb')
    patch_bin = open(so_path, 'rb')
    tfp_file = open(target_path, 'wb')
    tfp_file.write(cfg_bin.read())
    tfp_file.write(patch_bin.read())
    tfp_file.close()


    rmtree(fix_dir)
