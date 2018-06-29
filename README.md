# TigerFix

## Build

```shell
python3 setup.py sdist bdist_wheel 
```

## Installation

```shell
pip3 install dist/tigerfix-0.1.tar.gz
```

## Usage

* you should install the library and c/c++ files at first
    ```
    tfix install
    ```

* write your main program
    * include <tigerfix/def.h>
    * add `-ltfix` flag when linking

* write your patch file
    * include <tigerfix/dev.h>
    * compile it but without linking it
    ```
    gcc patch.c -c -fPIC -o patch.o
    ```
* generate patch file
    ```
    tfix gen -m main -p patch.o -o patch.tfp
    ```

* do hotfix
    * eval `pgrep main` , and you will get a pid(for example,10000)
    ```
    tfix fix 10000 patch.tfp
    ```
