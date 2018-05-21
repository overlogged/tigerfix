cmake_minimum_required(VERSION 3.10)
project(tigerfix)

add_subdirectory(src/cli)
add_subdirectory(src/lib)

install(FILES include/tigerfix/def.h DESTINATION include/tigerfix)
install(FILES include/tigerfix/dev.h DESTINATION include/tigerfix)

