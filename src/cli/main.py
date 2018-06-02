# packages
import argparse
import ptrace.debugger
import subprocess
import sys
import signal
import os

# utils
import utils.fix
import utils.gen

def main():
    # Argument Parsing

    # Initiating
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # Parser for Fixing
    fix_parser = subparsers.add_parser("fix", help="fix your process with generated patch")
    fix_parser.add_argument("pid", help="the process id of which process you want to hotfix", type=int)
    fix_parser.set_defaults(func=utils.fix.main)

    # Parser for Patch Generating
    gen_parser = subparsers.add_parser("gen", help="generate a fixing patch")    
    gen_parser.add_argument("-m", "--main", help="path of main program", default="../../examples/print_prime/obj/main")
    gen_parser.add_argument("-p", "--patch", help="path of patch file", default="../../examples/print_prime/patch/patch.so")
    # gen_parser.add_argument("-c", "--config", help="path of config", default="../../examples/print_prime/obj/config")
    # gen_parser.add_argument("-o", "--output", help="path of output", default="../../examples/print_prime/obj/patch.tfp")
    gen_parser.set_defaults(func=utils.gen.main)

    # Parser for Patch Cleaning
    # clean_parser = subparsers.add_parser("clean", help="remove generated patch")

    # exec function
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        parser.print_help()

if __name__ == "__main__":
    main()