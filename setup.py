#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='tigerfix',
    version='0.1',
    description='A hot fix tool for compiled languages such as c and c++.',
    long_description=open("README.rst").read(),
    url='https://github.com/NiceKingWei/tigerfix',
    license='GPL-3.0',
    keywords='hotfix c cpp',
    install_requires=['lief>=0.9.0', 'python-ptrace>=0.9.3'],
    author_email='nicekingwei@foxmail.com',
    packages=['tfix'],
    package_data={
        '': ['include/*.h', 'lib/*.c']
    },
    entry_points={
        'console_scripts': [
            'tfix = tfix.main:main'
        ]
    }
)
