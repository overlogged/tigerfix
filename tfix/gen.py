import os
import lief
import argparse
from shutil import rmtree

def hex_64bit(some_int):
    ans = format(some_int, "x")
    ans = ans.zfill(16) # 64 bit is 16 digits long in hex
    return ans

def do_link(obj_files,target_file):
    symbol_list = []
    for file in obj_files:
        libm_patch = lief.ELF.parse(file)
        for x in libm_patch.relocations:
            if x.symbol.name!='':
                symbol_list.append("--defsym %s=0xc0ffee"%x.symbol.name)

    command = "ld %s -shared -fno-plt %s -o %s" % (' '.join(obj_files),' '.join(symbol_list),target_file)
    os.system(command)
    # print(command)
    return target_file


def gen_config(main_path,so_path,config_path):
    libm_main = lief.ELF.parse(main_path)
    libm_patch = lief.ELF.parse(so_path)

    header_main = libm_main.header
    signal = str(header_main.file_type).split('.')[1]
    if signal == 'EXECUTABLE' :
        sig = 0
    else:
        sig = 1

    libm_symname = [x.name for x in libm_patch.symbols]
    libm_symname=set(libm_symname)

    fixfunc = []
    fixfunc_addr = []
    for x in libm_symname:
        if x[:4] == 'fix_':
            fixfunc_addr.append(hex_64bit(libm_patch.get_symbol(x).value))
            fixfunc.append(x[4:])

    func_addr = []
    for y in fixfunc:
        try:
            func_addr.append(hex_64bit(libm_main.get_symbol(y).value))
        except e:
            raise NameError("Symbols not found:%s" % e)

    globalname=[]
    for x in libm_symname:
        if(libm_patch.get_symbol(x).value==0xc0ffee):
            globalname.append(x)
    globaladdr=[]
    for y in globalname:
        globaladdr.append(hex_64bit(libm_main.get_symbol(y).value))
        # print(libm_main.get_symbol(y))

    got_addr=[]
    relocate=list(libm_patch.relocations)
    for name in globalname:
        for i in range(len(globalname)):
            if relocate[i].symbol.name==name:
                got_addr.append(hex_64bit((relocate[i].address)))

    configfile = open(config_path, "w")
    configfile.write("%d\n" % sig)
    configfile.write("%d\n" % len(globalname))
    for i in range(len(globaladdr)):
        configfile.write(got_addr[i] + ' ' + globaladdr[i] + '\n')
    configfile.write("%d\n" % len(func_addr))
    for i in range(len(func_addr)):
        configfile.write(func_addr[i] + ' ' + fixfunc_addr[i] + '\n')
    configfile.close()

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

    # link objects
    # todo: multiple patch files
    do_link(patch_path,so_path)

    # generating config file
    gen_config(main_path,so_path,config_path)

    # concat
    cfg_bin = open(config_path, 'rb')
    patch_bin = open(so_path, 'rb')
    tfp_file = open(target_path, 'wb')
    tfp_file.write(cfg_bin.read())
    tfp_file.write(patch_bin.read())
    tfp_file.close()

    rmtree(fix_dir)

# if __name__ == '__main__':
#     main()