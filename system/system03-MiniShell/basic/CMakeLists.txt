cmake_minimum_required(VERSION 3.16)
project(minishell_basic LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
file(GLOB_RECURSE MINISHELL_BASIC_SOURCES CONFIGURE_DEPENDS src/*.cpp)

add_executable(minishell-basic ${MINISHELL_BASIC_SOURCES})
target_compile_features(minishell-basic PRIVATE cxx_std_17)
target_compile_options(minishell-basic PRIVATE -Wall -Wextra -Wpedantic)

enable_testing()
foreach(EXAMPLE_NUMBER RANGE 1 8)
    add_test(
        NAME example${EXAMPLE_NUMBER}
        COMMAND ${CMAKE_COMMAND}
            -DPROGRAM=$<TARGET_FILE:minishell-basic>
            -DINPUT=${CMAKE_CURRENT_SOURCE_DIR}/tests/example${EXAMPLE_NUMBER}.in
            -DEXPECTED=${CMAKE_CURRENT_SOURCE_DIR}/tests/example${EXAMPLE_NUMBER}.out
            -DACTUAL=${CMAKE_CURRENT_BINARY_DIR}/example${EXAMPLE_NUMBER}.actual
            -P ${CMAKE_CURRENT_SOURCE_DIR}/tests/run_example.cmake
    )
endforeach()
