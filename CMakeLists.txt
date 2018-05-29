cmake_minimum_required(VERSION 3.10)
project(tigerfix)

add_subdirectory(src/cli)
add_subdirectory(src/lib)

install(FILES include/def.h DESTINATION include/tigerfix)
install(FILES include/dev.h DESTINATION include/tigerfix)

