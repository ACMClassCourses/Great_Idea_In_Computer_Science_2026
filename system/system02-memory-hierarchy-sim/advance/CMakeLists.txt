cmake_minimum_required(VERSION 3.16)

project(memory_hierarchy_simulator LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(memory_simulator
    src/simulator.cpp
    src/fifo.cpp
    src/lru.cpp
    src/clock.cpp
)

target_include_directories(memory_simulator PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src)

if(MSVC)
    target_compile_options(memory_simulator PRIVATE /W4)
else()
    target_compile_options(memory_simulator PRIVATE -Wall -Wextra -Wpedantic)
endif()

add_executable(memory-simulator src/main.cpp)
target_link_libraries(memory-simulator PRIVATE memory_simulator)

include(CTest)
if(BUILD_TESTING)
    add_executable(memory-simulator-tests tests/test_simulator.cpp)
    target_link_libraries(memory-simulator-tests PRIVATE memory_simulator)
    add_test(NAME memory-simulator-tests COMMAND memory-simulator-tests)
endif()
