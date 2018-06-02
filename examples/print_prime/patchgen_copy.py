import os
import lief
cmds = []

patch_path = "obj/patch.so"
main_path = "obj/main"
config_filename = "obj/config"
tiger_fix_patch_path = "obj/patch.tfp"

libm_main = lief.ELF.parse(main_path)
libm_patch = lief.ELF.parse(patch_path)

header_main = libm_main.header
signal = str(header_main.file_type).split('.')[1]
if signal == 'EXECUTABLE' :
    sig = 0
else:
    sig = 1
# cmds.append("objdump -R " + patch_path + " | grep global_data")
# cmds.append("nm " + main_path + " | grep global_data")
# cmds.append("objdump -R " + patch_path + " | grep print_global")
# cmds.append("nm " + main_path + " | grep print_global")
# cmds.append("nm " + main_path + " | grep is_prime")
# cmds.append("nm " + patch_path + " | grep fix_is_prime")

addresses = []
for cmd in cmds:
    line = os.popen(cmd).read()
    addresses.append(line.split(' ')[0])

configfile = open(config_filename, "w")
configfile.write("0\n")
configfile.write("2\n")
configfile.write(addresses[0] + ' ' + addresses[1] + '\n')
configfile.write(addresses[2] + ' ' + addresses[3] + '\n')
configfile.write("1\n")
configfile.write(addresses[4] + ' ' + addresses[5] + '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
configfile.close()
os.system("cat " + config_filename + ' ' + patch_path + ' > ' + tiger_fix_patch_path)