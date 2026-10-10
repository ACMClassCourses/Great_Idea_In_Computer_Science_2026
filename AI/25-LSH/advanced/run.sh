#!/bin/bash
# ============================================================================
#  LSH 提高版 —— 编译运行脚本
# ============================================================================
#
#  用法：
#    ./run.sh             # 编译学生版（用 lsh.cpp）并运行测试
#    ./run.sh solution    # 编译保底版（用 lsh_complete.cpp）并运行测试
#    ./run.sh build       # 只编译不运行
#    ./run.sh run         # 只运行已编译的程序
#
# ============================================================================

set -e

CXX=g++
CXXFLAGS="-std=c++17 -O2 -Wall -Wextra -Isrc"
DATA_DIR="${2:-../test/data}"
BINARY=test/test_lsh
ADV_BINARY=lsh_advanced

MODE="${1:-default}"

case "$MODE" in
    solution)
        echo "=== 用保底版 (solution/lsh_complete.cpp) 编译 ==="
        $CXX $CXXFLAGS src/mnist.cpp solution/lsh_complete.cpp \
            test/test_lsh.cpp -o $BINARY
        $CXX $CXXFLAGS src/mnist.cpp solution/lsh_complete.cpp \
            src/main.cpp -o $ADV_BINARY
        echo "=== 运行测试 ==="
        ./$BINARY "$DATA_DIR"
        ;;
    build)
        echo "=== 编译学生版 (src/lsh.cpp) ==="
        $CXX $CXXFLAGS src/mnist.cpp src/lsh.cpp \
            test/test_lsh.cpp -o $BINARY
        $CXX $CXXFLAGS src/mnist.cpp src/lsh.cpp \
            src/main.cpp -o $ADV_BINARY
        echo "编译完成。运行 ./run.sh run 来执行测试"
        ;;
    run)
        echo "=== 运行测试 ==="
        ./$BINARY "$DATA_DIR"
        ;;
    *)
        echo "=== 编译学生版 (src/lsh.cpp) ==="
        $CXX $CXXFLAGS src/mnist.cpp src/lsh.cpp \
            test/test_lsh.cpp -o $BINARY
        $CXX $CXXFLAGS src/mnist.cpp src/lsh.cpp \
            src/main.cpp -o $ADV_BINARY
        echo "=== 运行测试 ==="
        ./$BINARY "$DATA_DIR"
        ;;
esac
