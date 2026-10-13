cmake_minimum_required(VERSION 3.16)
project(BloomFilterApplication LANGUAGES CXX)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

add_executable(bloom_application main.cpp)
target_compile_features(bloom_application PRIVATE cxx_std_11)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(bloom_application PRIVATE -Wall -Wextra -Wpedantic)
endif()

enable_testing()
add_test(
    NAME application
    COMMAND ${Python3_EXECUTABLE} test.py $<TARGET_FILE:bloom_application>
)
set_tests_properties(
    application
    PROPERTIES WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)
