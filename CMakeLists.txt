# CMakeLists files in this project can
# refer to the root source directory of the project as ${HELLO_SOURCE_DIR} and
# to the root binary directory of the project as ${HELLO_BINARY_DIR}.
cmake_minimum_required (VERSION 2.8.11)
project (IDM)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=gnu99")

add_subdirectory (src)
add_subdirectory (demo)
