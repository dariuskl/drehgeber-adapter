# vim: ts=4:et:ft=cmake

cmake_minimum_required(VERSION 3.15)

project(mspmotor
    VERSION 0.1.0.0
    DESCRIPTION "driver example for MSP430 controllers"
    LANGUAGES CXX
)

set(CMAKE_EXPORT_COMPILE_COMMANDS On)
#set(CMAKE_CXX_CLANG_TIDY clang-tidy)
#set(CMAKE_CXX_CPPCHECK cppcheck)

add_executable(mspenc)

target_sources(mspenc
    PRIVATE main.cc
)

target_compile_features(mspenc
    PRIVATE cxx_std_17
)

target_compile_options(mspenc
    PRIVATE -fdiagnostics-color
            -Os -fno-rtti -fno-exceptions
            -ffunction-sections -fdata-sections -flto
            -Wextra -pedantic
)

target_include_directories(mspenc
    PRIVATE /opt/msp430/gcc/include
)

target_link_directories(mspenc
    PRIVATE /opt/msp430/gcc/include
)

target_link_options(mspenc
    PRIVATE LINKER:--gc-sections,-print-memory-usage
            LINKER:-Map=${CMAKE_BINARY_DIR}/mspenc.map
)

add_custom_command(TARGET mspenc POST_BUILD
    COMMAND ${CMAKE_OBJDUMP} -D $<TARGET_FILE:mspenc>
                > ${CMAKE_BINARY_DIR}/mspenc.S
    COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:mspenc>
                ${CMAKE_BINARY_DIR}/mspenc.hex
    BYPRODUCTS ${CMAKE_BINARY_DIR}/mspenc.S ${CMAKE_BINARY_DIR}/mspenc.hex
)
