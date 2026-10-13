cmake_minimum_required(VERSION 3.16)
project(reliable_transport_basic LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(reliable_transport_basic src/main.cpp)
