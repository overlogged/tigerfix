cmake_minimum_required(VERSION 3.10)
project(tigerfix-cli)

set(CMAKE_CXX_STANDARD 11)

add_executable(tfix main.cpp)

install(TARGETS tfix
        RUNTIME DESTINATION bin)