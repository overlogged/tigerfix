#!/bin/bash

clear
mkdir build
cd build
cmake ..
make
sudo make install
cd ..
rm -rf build
echo "======================================="
echo "Installation success!"
echo "======================================="