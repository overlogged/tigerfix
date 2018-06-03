import os
os.system("mkdir build")
os.chdir("build")
os.system("cmake ..")
os.system("make")

username = os.popen("whoami").read()
if username != "root":
    print(61 * "=")
    print("Root privileges is needed, please type in your ROOT password.")
    print(61 * "=")
    os.system("sudo make install")
else:
    os.system("make install")
os.chdir("..")
os.system("rm -rf build")
print(22 * "=")
print("Installation finished!")
print(22 * "=")
