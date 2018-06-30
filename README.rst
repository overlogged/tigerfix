TigerFix
=========

Build
---------
.. code::

    python3 setup.py sdist bdist_wheel 

Installation
------------

.. code::

    pip3 install dist/tigerfix-0.1.tar.gz

Usage
------------

+ you should install the library and c/c++ files at first

.. code::

    tfix install

+ write your main program
    + include <tigerfix/def.h>
    + add **-ltfix** flag when linking

+ write your patch file
    + include <tigerfix/dev.h>
    + use **extern** to get access to what you want to use in patch code
    + compile patch without linking it

    .. code ::

        gcc patch.c -c -fPIC -o patch.o

+ generate patch file

.. code ::

    tfix gen -m main -o patch.tfp patch.o 

+ do hotfix
    + eval **pgrep main** , and you will get a pid(for example,10000)
    
    .. code ::
    
        tfix fix 10000 patch.tfp
