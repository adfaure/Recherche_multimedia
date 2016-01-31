# Create a library called "Hello" which includes the source file "hello.cxx".
# The extension is already found. Any number of sources could be listed here.
add_library (Histogram SHARED histogram.c histogram.h  rdjpeg.c  rdjpeg.h)

target_include_directories(Histogram PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
