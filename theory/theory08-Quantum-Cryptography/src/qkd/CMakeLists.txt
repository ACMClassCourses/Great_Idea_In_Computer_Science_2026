cmake_minimum_required(VERSION 3.28)
project(QKD)

add_library(qubit_lib 
    src/quantum_lib/qubit.cpp
)

target_include_directories(
    qubit_lib
    PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

add_library(actors_lib
    src/actors/sender.cpp
    src/actors/receiver.cpp
    src/actors/listener.cpp 
)

target_include_directories(
    actors_lib
    PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_link_libraries(
    actors_lib
    qubit_lib
)

add_executable(qkd src/main.cpp)

target_link_libraries(
    qkd
    actors_lib
    qubit_lib
)
