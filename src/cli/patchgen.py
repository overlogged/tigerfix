import os
import lief
import argparse

def main():
    # Argument Parsing
    # Setting Argument Format
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--main", help="path of main process", default="../../examples/print_prime/obj/main")
    parser.add_argument("-p", "--patch", help="path of patch file", default="../../examples/print_prime/obj/patch.so")
    parser.add_argument("-c", "--config", help="path of config", default="../../examples/print_prime/obj/config")
    parser.add_argument("-o", "--output", help="path of output", default="../../examples/print_prime/obj/patch.tfp")

    # Getting Arguments from Input
    args = parser.parse_args()
    main_path = args.main
    patch_path = args.patch
    config_filename = args.config
    tiger_fix_patch_path = args.output

    # patch_path = "obj/patch.so"
    # main_path = "obj/main"
    # config_filename = "obj/config"
    # tiger_fix_patch_path = "obj/patch.tfp"

    libm_main = lief.ELF.parse(main_path)
    libm_patch = lief.ELF.parse(patch_path)

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
        fixfunc_addr.append(hex(libm_patch.get_symbol(x).value))
        fixfunc.append(x[4:])

    func_addr = []
    for y in fixfunc:
        try:
            func_addr.append(hex(libm_main.get_symbol(y).value))
        except as e:
            raise NameError("Symbols not found:%s" % e)

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

    # generating config file
    configfile = open(config_filename, "w")
    configfile.write("%d\n", % sig)
    configfile.write("%d\n" % len(globalname))
    for i in range(len(globaladdr)):
        configfile.write(got_addr[i] + ' ' + globaladdr[i] + '\n')
    configfile.write("%d\n" % len(func_addr))
    for i in range(len(func_addr)):
        configfile.write(func_addr[i] + ' ' + fixfunc_addr[i] + '\n')
    configfile.close()
    # os.system("cat " + config_filename + ' ' + patch_path + ' > ' + tiger_fix_patch_path)
    tfp_file = open(tiger_fix_patch_path, 'wb')
    cfg_bin = open(config_filename, 'rb')
    patch_bin = open(patch_path, 'rb')
    tfp_file.write(cfg_bin.read())
    tfp_file.write(patch_bin.read())
    tfp_file.close()

if __name__ == '__main__':
    main()