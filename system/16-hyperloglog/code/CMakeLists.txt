cmake_minimum_required(VERSION 3.16)
project(hll_student LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(hll main.cpp)
add_executable(unit_tests unit_tests.cpp)
