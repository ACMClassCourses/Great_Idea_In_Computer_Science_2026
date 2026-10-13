# Advance：页面置换策略比较

## 要做什么

在 Basic 的 FIFO 基础上完成 LRU 和 CLOCK，并展示三种算法的逐步状态与汇总统计。请先阅读根目录 `README.md` 中的 Advance 部分；本目录的已有代码提供公共数据结构、输入验证、CMake 和测试框架；FIFO 需复用你在 Basic 中完成的实现。

需要完成的代码位于：

- `src/fifo.cpp`：将 Basic 的 FIFO 接到统一结果接口，补齐逐步状态与统计。
- `src/lru.cpp`：LRU 的命中更新、装入和淘汰。
- `src/clock.cpp`：CLOCK 的访问位、循环指针、扫描和淘汰。
- `src/main.cpp`：每种算法的统计信息和最终对比表。

只修改标有 `TODO` 的位置。保留已有函数接口，以便测试程序调用。

## 输入与输出

输入沿用 OJ 3275 的格式：第一行是 `c n`，第二行是 `n` 个页面编号。例如：

```text
3 7
1 2 3 1 4 2 5
```

程序应分别输出 FIFO、LRU、CLOCK 的每一步状态。CLOCK 还应输出访问位和指针。最后输出总访问次数、命中次数、未命中次数、命中率和三种算法的对比表。

统一示例的未命中次数应为：FIFO 5、LRU 6、CLOCK 5。

## 编译、运行与测试

在本目录执行：

```bash
cmake -S . -B build
cmake --build build
printf '3 7\n1 2 3 1 4 2 5\n' | ./build/memory-simulator
ctest --test-dir build --output-on-failure
```

初始框架可以编译，但由于 TODO 尚未完成，测试不会全部通过。完成后应看到：

```text
100% tests passed, 0 tests failed
```

## 完成标准

- LRU 和 CLOCK 严格遵守根 README 中的规则。
- 每一步的命中、淘汰、缓存状态以及 CLOCK 状态均可核对。
- 统一示例、边界情况和 Belady 异常测试全部通过。
- 完成根 README 中 G1–G7 要求的实验、阅读笔记和讲解材料。
