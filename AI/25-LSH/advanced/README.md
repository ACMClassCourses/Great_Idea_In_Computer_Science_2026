# LSH 近似最近邻检索（提高版）

> 一句话：在基础版上加了模块化、k-NN、命令行参数和测试，需要你实现 k-NN 查询函数，有保底方案。

## 这是个啥？

这个项目的核心是 **LSH（局部敏感哈希）**——一种快速找"最相似数据"的算法。数据集用的是 MNIST（手写数字图片）。

提高版和基础版做的是同一件事——用 LSH 找最相似的训练图片来分类测试图片。但区别在于：

- **代码拆成了多个文件**（`mnist.cpp` 管读取，`lsh.cpp` 管算法，`main.cpp` 管流程）
- **1-NN 已经实现好**，开箱即用
- **k-NN 需要你来写**（这是主要挑战）
- **有命令行参数**，不用改代码就能调参数
- **有测试用例**，帮你验证写得对不对

## 学完你能会啥？

- 会写多文件 C++ 项目
- 理解 k-NN（k 最近邻）和多数投票
- 会用 `std::partial_sort` 等标准库算法
- 会写简单的命令行参数解析
- 会写和运行测试用例
- 理解 LSH 的多探测（multi-probe）机制

## 先看效果

### 1-NN 模式（开箱即用）

```bash
g++ -std=c++17 -O2 -Isrc src/mnist.cpp src/lsh.cpp src/main.cpp -o lsh_advanced
./lsh_advanced ../test/data -n 1000
```

你会看到准确率约 95%~96%，跟基础版差不多，但代码结构清晰多了。

### k-NN 模式（需要你实现 query_knn）

```bash
./lsh_advanced ../test/data -k 5 -n 1000
```

k-NN 取最近 k 个邻居投票决定结果，比 1-NN 更稳定。

## 你需要准备

- g++ 7 以上（支持 C++17）
- MNIST 数据文件（在 `../test/data/` 目录）
- 基础版跑通过（理解了 LSH 的基本流程）

## 项目结构

```
advanced/
├── README.md                  ← 你正在看的
├── run.sh                     ← 一键编译运行脚本
├── src/
│   ├── mnist.h                ← MNIST 数据结构定义
│   ├── mnist.cpp              ← MNIST 文件读取（已实现）
│   ├── lsh.h                  ← LSH 接口定义（含 k-NN 声明）
│   ├── lsh.cpp                ← LSH 实现（1-NN 已实现，k-NN 是 TODO）
│   └── main.cpp               ← 主程序（已实现，含参数解析和 k-NN 调用）
├── solution/
│   └── lsh_complete.cpp       ← 保底参考实现（全部实现好）
└── test/
    └── test_lsh.cpp            ← 测试用例（4 个）
```

### 模块依赖关系

```
main.cpp ──调用──> mnist.cpp（读数据）
    │
    └───────────> lsh.cpp（建索引、查询）
```

`lsh.cpp` 只管算法，不管数据怎么读。`main.cpp` 负责把数据喂给 `lsh.cpp`。

## 三步跑起来

### 第 1 步：编译

```bash
cd advanced
g++ -std=c++17 -O2 -Isrc src/mnist.cpp src/lsh.cpp src/main.cpp -o lsh_advanced
```

或者用脚本：

```bash
cd advanced
./run.sh build
```

### 第 2 步：运行

```bash
# 1-NN 模式，测前 1000 张
./lsh_advanced ../test/data -n 1000

# 全量测试（慢，约 30 秒）
./lsh_advanced ../test/data
```

### 第 3 步：运行测试

```bash
g++ -std=c++17 -O2 -Isrc src/mnist.cpp src/lsh.cpp test/test_lsh.cpp -o test/test_lsh
./test/test_lsh ../test/data
```

或者用脚本：

```bash
./run.sh
```

**你应该看到**：测试 1~3 通过，测试 4 跳过（因为 `query_knn` 还没实现）。

## 你要做的任务

### 阶段 1：先跑通原样

1. 编译运行 1-NN 模式，确认能跑、准确率合理
2. 运行测试，确认测试 1~3 通过、测试 4 跳过
3. 读一遍 `lsh.h` 和 `lsh.cpp`，理解 1-NN 的流程

### 阶段 2：核心挑战

#### 挑战任务 1：实现 k-NN 查询（必做）

在 `src/lsh.cpp` 末尾的 `query_knn()` 函数里，把 TODO 替换成你的实现。

**目标**：给定查询图片和整数 k，返回候选集合里距离最近的 k 张训练图片的编号和距离。

**提示**：

1. 前半部分（收集候选）跟 `query()` 一模一样，直接复制
2. 后半部分需要算每个候选的距离，然后取前 k 个
3. 推荐做法：
   - 用 `std::vector<std::pair<std::int64_t, int>>` 存 (距离, 编号)
   - 用 `std::partial_sort` 排前 k 个（比全排序快）
   - 取前 `min(k, 候选数)` 个填入 `result`
4. 距离计算跟 `query()` 里一样：平方欧氏距离，不开根号

**验证**：实现后运行测试，测试 4 应该通过。

**保底方案**：如果实在写不出来，用 `solution/lsh_complete.cpp` 替换 `src/lsh.cpp` 编译：

```bash
g++ -std=c++17 -O2 -Isrc src/mnist.cpp solution/lsh_complete.cpp src/main.cpp -o lsh_advanced
```

这样程序照样能跑，只是 k-NN 不是你写的。先跑通，有空再回来自己写。

#### 挑战任务 2：用 k-NN 多数投票分类

`main.cpp` 里已经写好了 k-NN 的调用和投票逻辑，你只要实现 `query_knn()` 就能用：

```bash
./lsh_advanced ../test/data -k 5 -n 1000
```

**思考**：k=5 的准确率跟 k=1 比怎么样？k=10 呢？k 不是越大越好，试试找出最优的 k。

### 阶段 3：选做扩展

#### 选做 1：加更多命令行参数

`main.cpp` 已经支持 `-k`、`-n`、`--no-detail`。试着加 `-L`（表数）、`-K`（位数）、`-seed`（种子）。

提示：在参数解析的 `for` 循环里加 `else if (arg == "-L" && i + 1 < argc)` 分支，用 `std::stoi` 读整数。

#### 选做 2：加暴力搜索对比

`main.cpp` 里有一个 `brute_force_nn()` 函数，注释掉了对比代码。取消注释，对比 LSH 和暴力搜索在前 100 张上的准确率差异。

#### 选做 3：加新的测试用例

在 `test/test_lsh.cpp` 里加一个测试：验证 k-NN 返回的 k 个结果确实是按距离从小到大排的。

## 卡住了看这里

### query_knn 编译报错

检查 `lsh.h` 里 `KnnResult` 的字段名是不是跟你的代码一致（`indices`、`distances`、`candidate_count`）。

### k-NN 准确率比 1-NN 低

检查投票逻辑。`main.cpp` 里的投票：对 k 个邻居的标签计数，取出现最多的。如果 k 是偶数可能出现平票，当前代码取标签号小的——这是可以的，不是 bug。

### 测试 3（MNIST）很慢

正常。MNIST 有 6 万训练 + 1 万测试，建索引 3 秒，查询约 30 秒。测试 1 和 2 很快（几秒）。

### 改了 lsh.cpp 但结果没变

确认你改的是 `advanced/src/lsh.cpp`，不是 `basic/lsh_basic.cpp`。编译命令里的路径也要对。

### 编译报 multiple definition

你不能同时编译 `lsh.cpp` 和 `solution/lsh_complete.cpp`——它们定义了同样的函数。二选一。

## 自查清单

- [ ] 1-NN 模式能跑，准确率约 96%
- [ ] 测试 1（自查询）通过
- [ ] 测试 2（大规模 2D）通过
- [ ] 测试 3（MNIST）通过
- [ ] **实现了 `query_knn`，测试 4 通过**
- [ ] k-NN 模式能跑（`-k 5`）
- [ ] 试了至少 3 个不同的 k 值，记录了准确率
- [ ] 至少完成了一个选做任务

## 想回看基础版？

如果觉得提高版的模块化有点绕，或者 `query_knn` 写不动，可以先回基础版看看单文件版的 `query()` 怎么写的。基础版在一个文件里，跟着 `main()` 往下读，逻辑更连贯。

基础版在 `../basic/` 目录，代码全在 `lsh_basic.cpp` 一个文件里。
