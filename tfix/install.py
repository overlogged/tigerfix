from pkg_resources import resource_filename
from os import system,geteuid,execlp,path,mkdir
from shutil import copy2,rmtree
from os import remove,rmdir
from . import root
import sys

prefix ='/usr'
dir_lib = prefix + '/lib'
dir_include = prefix + '/include/tigerfix'

def main(args):
    root.get_root()
    patch_c = resource_filename(__name__, 'lib/patch.c')
    patch_so = patch_c.replace('lib/patch.c','lib/libtfix.so')
    system("gcc %s -shared -fPIC -O2 -ldl -o %s" % (patch_c,patch_so))
    dev_h = resource_filename(__name__, 'include/dev.h')
    def_h = resource_filename(__name__, 'include/def.h')

    copy2(patch_so,dir_lib)
    print('runtime library installed.')
    
    if not path.exists(dir_include):
        mkdir(dir_include)

    copy2(dev_h,dir_include)
    copy2(def_h,dir_include)
    print('c/c++ header files installed.')

def clean(args):
    root.get_root()

    try:
        remove(dir_lib+'/libtfix.so')
    except:
        None
    finally:
        try:
            rmtree(dir_include)
        except:
            None