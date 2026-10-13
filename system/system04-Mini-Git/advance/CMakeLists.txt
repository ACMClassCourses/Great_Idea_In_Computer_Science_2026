cmake_minimum_required(VERSION 3.16)
project(minigit LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
file(GLOB_RECURSE MINIGIT_SOURCES CONFIGURE_DEPENDS src/*.cpp)

add_executable(minigit ${MINIGIT_SOURCES})
target_include_directories(minigit PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_compile_features(minigit PRIVATE cxx_std_11)
target_compile_options(minigit PRIVATE -Wall -Wextra -Wpedantic)

enable_testing()
foreach(EXAMPLE_NUMBER RANGE 1 5)
    add_test(
        NAME example${EXAMPLE_NUMBER}
        COMMAND ${CMAKE_COMMAND}
            -DPROGRAM=$<TARGET_FILE:minigit>
            -DINPUT=${CMAKE_CURRENT_SOURCE_DIR}/tests/example${EXAMPLE_NUMBER}.in
            -DEXPECTED=${CMAKE_CURRENT_SOURCE_DIR}/tests/example${EXAMPLE_NUMBER}.out
            -DACTUAL=${CMAKE_CURRENT_BINARY_DIR}/example${EXAMPLE_NUMBER}.actual
            -P ${CMAKE_CURRENT_SOURCE_DIR}/tests/run_example.cmake
    )
endforeach()
