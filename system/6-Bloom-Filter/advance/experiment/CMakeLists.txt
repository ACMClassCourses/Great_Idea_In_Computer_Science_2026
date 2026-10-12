cmake_minimum_required(VERSION 3.16)
project(BloomFilterExperiment LANGUAGES CXX)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

add_executable(main main.cpp)
set_target_properties(main PROPERTIES
    CXX_STANDARD 11
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(main PRIVATE -Wall -Wextra -Wpedantic)
endif()

enable_testing()
add_test(
    NAME experiment
    COMMAND ${Python3_EXECUTABLE} test.py $<TARGET_FILE:main>
)
set_tests_properties(
    experiment
    PROPERTIES WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)
