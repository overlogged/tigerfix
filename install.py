import os
import argparse

cwd = os.getcwd()
build_folder = "build"

def print_prompt(prompt):
    print(len(prompt) * "=")
    print(prompt)
    print(len(prompt) * "=")

def main():
    # ArgPasring
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    auto_parser = subparsers.add_parser("auto", help = "automatically make, install and clean")
    auto_parser.set_defaults(func=auto_install)

    make_parser = subparsers.add_parser("make", help="build from source code")
    make_parser.set_defaults(func=make)

    install_parser = subparsers.add_parser("install", help="install builded files")
    install_parser.set_defaults(func=install)

    clean_parser = subparsers.add_parser("clean", help="remove builded files")
    clean_parser.set_defaults(func=clean)
    
    # Parsing and Executing
    args = parser.parse_args()
    try:
        args.func()
    except AttributeError:
        parser.print_help()

def make():
    os.chdir(cwd)
    os.system("mkdir build")
    os.chdir(build_folder)
    os.system("cmake ..")
    os.system("make")
    print_prompt("Make finished!")

def install():
    username = os.popen("whoami").read()

    if username != "root":
        print(61 * "=")
        print("Root privileges is needed, please type in your ROOT password.")
        print(61 * "=")
        os.system("sudo make install")
    else:
        os.system("make install")
    
    print_prompt("Installation finished!")
    

def clean():
    os.chdir(cwd)
    os.system("rm -rf " + build_folder)
    print_prompt("Cleaning finished!")

def auto_install():
    make()
    install()
    clean()

main()