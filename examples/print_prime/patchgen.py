import os
cmds = []

patch_path = "obj/patch.so"
exec_path = "obj/main"
config_filename = "obj/config"
tiger_fix_patch_path = "obj/patch.tfp"

cmds.append("objdump -R " + patch_path + " | grep global_data")
cmds.append("nm " + exec_path + " | grep global_data")
cmds.append("objdump -R " + patch_path + " | grep print_global")
cmds.append("nm " + exec_path + " | grep print_global")
cmds.append("nm " + exec_path + " | grep is_prime")
cmds.append("nm " + patch_path + " | grep fix_is_prime")

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