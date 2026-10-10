# 常见报错与解决

## 编译问题

### `error: 'std::filesystem' has not been declared`

你的 g++ 版本太老或者没开 C++17。确认：

```bash
g++ --version    # 需要 7.0 以上
```

编译命令里要有 `-std=c++17`。如果 g++ 版本太低，升级或者用更高版本的编译器。

### `error: 'INT16_MAX' was not declared`

忘了 `#include <cstdint>`。基础版单文件已经包含了，如果你改过代码检查一下有没有删掉 include。

### `multiple definition of 'LshIndex::query_knn(...)'`

你不能同时编译 `lsh.cpp` 和 `solution/lsh_complete.cpp`——它们定义了同样的函数。二选一：

```bash
# 学生版（你自己实现的）
g++ ... src/lsh.cpp src/main.cpp ...

# 保底版（参考实现）
g++ ... solution/lsh_complete.cpp src/main.cpp ...
```

### 编译很慢

- 加 `-O0`（零优化）能加快编译，但运行会慢
- 基础版只有一个文件，编译应该很快（1~2 秒）
- 提高版 3 个文件，也就几秒

### `warning: unused parameter 'point'`

提高版 `lsh.cpp` 里 `query_knn` 还没实现时会有这个警告。实现了就没了。如果你不想看到它，可以加 `(void)point;`（代码里已经加了）。

## 运行问题

### `打不开 MNIST 文件` / `无法打开 MNIST 文件`

**最常见的问题**。大概率是路径不对。

程序默认找 `../test/data`，也就是当前目录的上一层有个 `test/data`。如果你不在 `basic/` 或 `advanced/` 目录下运行，路径就不对。

解决方法——用绝对路径：

```bash
# 基础版
./lsh_basic /完整/路径/到/25-LSH/test/data

# 提高版
./lsh_advanced /完整/路径/到/25-LSH/test/data
```

或者先 `cd` 到对应目录再运行：

```bash
cd basic
./lsh_basic ../test/data
```

### `MNIST 文件格式不正确` / `invalid MNIST files`

数据文件损坏或不是标准 MNIST 格式。检查文件大小：

```
train-images.idx3-ubyte  应该是 47040016 字节
train-labels.idx1-ubyte  应该是 60008 字节
t10k-images.idx3-ubyte   应该是 7840016 字节
t10k-labels.idx1-ubyte   应该是 10008 字节
```

```bash
ls -l test/data/
```

如果文件大小不对，重新获取 MNIST 数据集。

### `索引还没建立，请先调用 build()`

你在没调 `build()` 的情况下就调了 `query()`。检查 `main()` 里有没有先 `index.build(...)` 再 `index.query(...)`。

### `LSH 参数不合法`

检查 `LshConfig` 的值：
- `table_count` 必须 > 0
- `bits_per_table` 必须 > 0 且 <= 20

### 运行很慢 / 卡住了

- 确认编译时加了 `-O2`（不加会慢 10 倍）
- 基础版测 1000 张约 10~20 秒
- 提高版测全部 10000 张约 30 秒
- 如果等了 2 分钟还没结束，可能是 `-O2` 忘加了

## 准确率问题

### 准确率低于 80%

检查这几件事：

1. **距离计算有没有写对**：应该是平方欧氏距离 `diff * diff` 累加，不是开根号
2. **标签有没有搞反**：应该是 `train.labels[result.index]` 跟 `test.labels[i]` 比
3. **签名计算有没有写反**：`dot >= 0` 设 1，`dot < 0` 不设（保持 0）
4. **多探测有没有加**：候选太少时不查相邻桶会漏掉近邻
5. **随机种子有没有固定**：如果每次结果不一样，检查 `seed` 是不是固定的

### 准确率每次运行不一样

随机种子没固定。`LshConfig` 里的 `seed` 应该是个固定常数（比如 42），不是随机生成的。

### k-NN 准确率比 1-NN 低

可能原因：
1. `query_knn` 返回的结果没按距离排序——检查是不是用了 `partial_sort`
2. 投票逻辑有 bug——检查 `main.cpp` 里的 `votes` 数组
3. k 太大或太小——试 k=3、5、7

### 准确率突然降到 10%

差不多就是随机猜了。大概率是 `query()` 返回了 -1（没找到候选），或者标签对不上。加个 `std::cout` 打印前几张的 `result.index` 和 `result.candidate_count` 看看。

## 测试问题

### 测试 4 跳过了

正常。`query_knn` 还没实现，测试代码里 `catch` 了 `logic_error` 就跳过了。实现了 `query_knn` 后这个测试才会真正运行。

### 测试 3 很慢

正常。MNIST 测试要建索引（3 秒）+ 查 1 万张（30 秒）。测试 1 和 2 很快。

### 测试编译报错

检查 include 路径：编译命令里要有 `-Isrc`（提高版）或 `-Iadvanced/src`。测试文件 `#include "lsh.h"` 和 `#include "mnist.h"` 需要找到这些头文件。

## 其他问题

### 看不懂代码

1. 先跑通，别先纠结看懂
2. 从 `main()` 开始看，跟着执行顺序走
3. 注释写得比较多，先看注释
4. 基础版单文件比提高版好懂，可以先看基础版
5. 实在不懂就问同学或助教

### Windows 下 PowerShell 跑不了

- 用 WSL（Windows Subsystem for Linux）最省事
- 或者用 MinGW 编译：`g++ -std=c++17 -O2 -o lsh_basic.exe lsh_basic.cpp`
- 路径用反斜杠 `\` 或者用正斜杠 `/` 都行

### `./run.sh` 权限不够

```bash
chmod +x advanced/run.sh
./advanced/run.sh
```
