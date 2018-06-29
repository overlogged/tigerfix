# packages
import argparse
import ptrace.debugger
import subprocess
import sys
import signal
import os

# utils
from . import fix
from . import gen
from . import install

def check(f):
    def g(arg):
        if not (os.path.exists('/usr/lib/libtfix.so') and os.path.exists('/usr/include/dev.h') and os.path.exists('/usr/include/def.h')):
            print('please install the runtime library and c/c++ header files at first.')
            install.main(arg)
        f(arg)
    return g

def main():
    # Argument Parsing

    # Initiating
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # Parser for Installation
    install_parser = subparsers.add_parser("install",help="install the runtime library and c/c++ header files")
    install_parser.set_defaults(func=install.main,sub=install_parser)

    uninstall_parser = subparsers.add_parser("uninstall",help="uninstall the runtime library and c/c++ header files")
    uninstall_parser.set_defaults(func=install.clean,sub=uninstall_parser)

    # Parser for Fixing
    fix_parser = subparsers.add_parser("fix", help="fix your process with generated patch")
    fix_parser.add_argument("pid", help="the process id of which process you want to hotfix", type=int)
    fix_parser.add_argument("patch",help="the path of the patch file")
    fix_parser.set_defaults(func=check(fix.main),sub=fix_parser)

    # Parser for Patch Generating
    gen_parser = subparsers.add_parser("gen", help="generate a fixing patch")    
    gen_parser.add_argument("patch",nargs='+', help="path of patch file")
    gen_parser.add_argument("-m",dest="main", help="path of main program")
    gen_parser.add_argument("-o",dest="object",help="target file")
    gen_parser.set_defaults(func=check(gen.main),sub=gen_parser)

    # Parser for Patch Cleaning
    # clean_parser = subparsers.add_parser("clean", help="remove generated patch")

    # exec function
    args = parser.parse_args()
    func = None
    try:
        func = args.func
    except AttributeError:
        parser.print_help()
    finally:
        try:
            if not func is None:
                func(args)
        except AttributeError:
            args.sub.print_help()

if __name__ == "__main__":
    main()