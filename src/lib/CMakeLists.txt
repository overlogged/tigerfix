cmake_minimum_required(VERSION 3.10)
project(tigerfix-lib)

set(LIBRARY_SRC patch.c)
add_library(tfix-dynamic SHARED ${LIBRARY_SRC})
add_library(tfix-static STATIC ${LIBRARY_SRC})
set_target_properties(tfix-dynamic PROPERTIES OUTPUT_NAME "tfix")
set_target_properties(tfix-static PROPERTIES OUTPUT_NAME "tfix")

target_compile_options(tfix-dynamic PRIVATE -O2)
target_link_libraries(tfix-dynamic PRIVATE dl)

target_compile_options(tfix-static PRIVATE -O2)

install(TARGETS tfix-dynamic tfix-static
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib)
