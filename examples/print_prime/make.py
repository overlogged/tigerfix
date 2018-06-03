import argparse
import os

def main():
    # ArgPasring
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    make_parser = subparsers.add_parser("dynamic", help="generate Makefile for dynamic library")
    make_parser.set_defaults(func=dynamic)

    clean_parser = subparsers.add_parser("static", help="generate Makefile for static library")
    clean_parser.set_defaults(func=static)

    # Parsing and Executing
    args = parser.parse_args()
    try:
        args.func()
    except AttributeError:
        parser.print_help()

def dynamic():
    os.system("cp Makefile_dynamic Makefile")

def static():
    os.system("cp Makefile_static Makefile")

main()    