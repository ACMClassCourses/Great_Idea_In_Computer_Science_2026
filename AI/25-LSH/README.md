# LSH 近似最近邻检索

> 用局部敏感哈希（LSH）在 MNIST 数据集上做近似最近邻检索，从入门到进阶，两个版本任你选。

## 1 分钟选版本

| | 基础版 | 提高版 |
|---|---|---|
| **适合谁** | 刚学完循环函数数组的新生 | 基础版跑通了，想挑战一下 |
| **难度** | ★☆☆ 简单 | ★★☆ 有一点挑战 |
| **完成时间** | 1~3 小时 | 4~8 小时 |
| **文件数** | 1 个 | 6 个（含测试和保底方案）|
| **要自己写吗** | 要写 2 个核心函数 | 要实现 k-NN（有保底方案）|
| **准确率** | ~96% | ~96%（1-NN）/可调参 |
| **亮点** | 写 2 个核心函数、ASCII 艺术显示 | 模块化、命令行参数、测试用例 |

**怎么选？**

- **基础版**：想快速理解 LSH 是什么、跑起来有成就感 → 进 [`basic/`](basic/README.md)
- **提高版**：已经懂了基本流程，想写点代码、学多文件项目 → 进 [`advanced/`](advanced/README.md)

两个版本用的是同一套 MNIST 数据（在 `test/data/`），不用担心数据要下两次。

## 这是个啥项目？

这个项目的核心是 **LSH（局部敏感哈希）**——一种用来快速找"最相似的数据"的算法。

应用场景用的是 MNIST 数据集（6 万张训练图片 + 1 万张测试图片，每张 28×28 像素的手写数字图片）。程序要做的事情：

1. 读训练图片，建 LSH 索引（把相似的图片分到同一个"桶"里）
2. 对每张测试图片，用 LSH 快速找到候选（不用翻全部 6 万张）
3. 在候选里算精确距离，取最近的一张
4. 用最近训练图片的标签来"猜"测试图片是几
5. 输出准确率

LSH 是工业界做"以图搜图""推荐系统"的底层技术之一。这个项目是它的简化教学版。

## 快速开始

```bash
# 基础版（编译后先跑一次看 18% 准确率，再实现 TODO 提升到 95%）
cd basic
g++ -std=c++17 -O2 -o lsh_basic lsh_basic.cpp
./lsh_basic ../test/data          # TODO 未实现，准确率约 18%
# 打开 lsh_basic.cpp 实现 TODO 1 和 TODO 2，重新编译运行 → 95%+

# 提高版（1-NN 模式，开箱即用）
cd advanced
g++ -std=c++17 -O2 -Isrc src/mnist.cpp src/lsh.cpp src/main.cpp -o lsh_advanced
./lsh_advanced ../test/data -n 1000
```

两个版本都只需要 g++ 和项目自带的 MNIST 数据文件，不需要装别的。

## 目录结构

```
25-LSH/
├── README.md                          ← 你在看的这个
├── 局部敏感哈希（LSH）完整文档.md         ← LSH 原理详解（想深入就看这个）
├── basic/                             ← 基础版
│   ├── README.md
│   └── lsh_basic.cpp                  ← 单文件，需实现 2 个核心函数
├── advanced/                          ← 提高版
│   ├── README.md
│   ├── run.sh
│   ├── src/                           ← 模块化代码（mnist + lsh + main）
│   │   ├── mnist.h  mnist.cpp
│   │   ├── lsh.h    lsh.cpp           ← 需实现 query_knn
│   │   └── main.cpp
│   ├── solution/
│   │   └── lsh_complete.cpp           ← 保底参考实现
│   └── test/
│       └── test_lsh.cpp               ← 4 个测试用例
├── src/                               ← 原始项目代码（完整版）
│   ├── main.cpp  lsh.h  lsh.cpp
│   └── mnist.h   mnist.cpp
├── test/                              ← MNIST 数据 + 原始测试
│   ├── data/
│   │   ├── train-images.idx3-ubyte
│   │   ├── train-labels.idx1-ubyte
│   │   ├── t10k-images.idx3-ubyte
│   │   └── t10k-labels.idx1-ubyte
│   ├── test_lsh.cpp
│   └── run_tests.ps1
└── docs/                              ← 文档
    ├── implement_guide.md              ← 原始实现指南
    ├── comparison.md                   ← 基础版 vs 提高版对比
    └── troubleshooting.md             ← 常见报错解决
```

## 学习路径建议

```
基础版 README → 实现距离函数 + 多探测 → 准确率到 95% → 
→ 提高版 README → 读代码 → 实现 query_knn → 跑测试 → 
→ 看完整文档深入理解原理
```

别一上来就看提高版。基础版虽然简单，但能帮你建立对 LSH 流程的直觉。

## 关于原始项目

`src/` 目录是完整的原始项目代码，供参考。它功能最全（1-NN + 多探测 + 计时），但没有挑战任务。基础版和提高版都是从它简化/改造来的。

想看原始项目怎么跑：

```bash
g++ -std=c++17 -O2 -Isrc src/lsh.cpp src/mnist.cpp src/main.cpp -o lsh_orig
./lsh_orig test/data
```

## 更多文档

- [LSH 完整原理文档](局部敏感哈希（LSH）完整文档.md)——从"为什么需要 LSH"到参数调优，写得通俗
- [基础版 vs 提高版详细对比](docs/comparison.md)——功能矩阵、代码差异、适合人群
- [常见报错与解决](docs/troubleshooting.md)——编译、运行、准确率问题汇总
- [原始实现指南](docs/implement_guide.md)——从零开始写 LSH 的详细步骤

## 环境要求

- **操作系统**：Linux / macOS / Windows（WSL 或 MinGW）
- **编译器**：g++ 7+ 或 clang++ 7+（需支持 C++17）
- **其他**：无外部依赖，只用 C++ 标准库

检查你的环境：

```bash
g++ --version    # 需要 7.0 以上
```
