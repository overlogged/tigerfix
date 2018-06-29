from os import system,geteuid,execlp
import sys

def get_root():
    if geteuid():
        args = [sys.executable] + sys.argv
        execlp('sudo', 'sudo', *args)