cmake_minimum_required(VERSION 3.16)
project(minishell_advance LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# 单文件工程：所有代码都写在 src/main.cpp 里，提交到 OJ 的也是这一个文件。
add_executable(minishell-advance src/main.cpp)
target_compile_features(minishell-advance PRIVATE cxx_std_17)
target_compile_options(minishell-advance PRIVATE -Wall -Wextra -Wpedantic)

enable_testing()
foreach(EXAMPLE_NUMBER RANGE 1 8)
    add_test(
        NAME example${EXAMPLE_NUMBER}
        COMMAND ${CMAKE_COMMAND}
            -DPROGRAM=$<TARGET_FILE:minishell-advance>
            -DINPUT=${CMAKE_CURRENT_SOURCE_DIR}/tests/example${EXAMPLE_NUMBER}.in
            -DEXPECTED=${CMAKE_CURRENT_SOURCE_DIR}/tests/example${EXAMPLE_NUMBER}.out
            -DACTUAL=${CMAKE_CURRENT_BINARY_DIR}/example${EXAMPLE_NUMBER}.actual
            -P ${CMAKE_CURRENT_SOURCE_DIR}/tests/run_example.cmake
    )
endforeach()
