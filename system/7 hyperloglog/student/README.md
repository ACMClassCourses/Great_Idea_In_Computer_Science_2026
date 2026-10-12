# HyperLogLog：用固定空间估计不同元素数量

## 1. 项目目标

很多系统需要统计一段数据中出现了多少个不同元素。例如网站的独立访客数、日志中的不同设备数，以及一段时间内出现过的不同用户数。

使用 `std::set` 或 `std::unordered_set` 可以得到精确答案，但集合会随着不同元素数量持续增长。HyperLogLog（HLL）只保存一组很小的统计量，用固定空间给出近似结果。

本项目分成两个部分：

- **Basic** 是一道在 OJ 上评测的算法题。主程序和输入输出框架已经提供，学生只需实现 HLL 的主体算法。
- **Hard** 是 HLL 的应用任务。学生需要统计最近若干时间桶中出现过的不同用户，不设置排行榜，也不要求设计精确集合与 HLL 之间的自适应切换。

Basic 和 Hard 均使用 C++17。

---

## 2. HLL 算法原理

### 2.1 从哈希值观察稀有事件

将一个元素映射成均匀随机的 64 位二进制数。一个随机数第一位就是 `1` 的概率是 `1/2`，以 `01` 开头的概率是 `1/4`，以 `001` 开头的概率是 `1/8`。

定义 `rho` 为从左向右第一次出现 `1` 的位置：

```text
1xxxx...   rho = 1
01xxx...   rho = 2
001xx...   rho = 3
0001x...   rho = 4
```

`rho` 很大是一件罕见的事。观察的不同元素越多，越可能遇到较大的 `rho`，因此最大 `rho` 可以反映数据规模。

只保存一个最大值会非常不稳定。HLL 使用参数 `p` 把数据分成 `m = 2^p` 组，每组对应一个 register。多个 register 的结果组合起来，可以显著降低随机波动。

### 2.2 register 下标与 rho

设元素哈希后的值为 `h`：

- `h` 的最高 `p` 位作为 register 下标；
- 剩余 `64-p` 位用于计算 `rho`；
- 如果剩余部分全部为 0，则 `rho = 64-p+1`。

每次加入元素时只需执行：

```cpp
registers[index] = max(registers[index], rho_value);
```

同一个元素总会得到相同的哈希、下标和 `rho`，所以重复加入不会不断增加统计结果。

### 2.3 基数估计

设第 `i` 个 register 的值为 `M[i]`，基本估计式为：

```text
E = alpha_m * m^2 / sum(2^(-M[i]))
```

其中：

```text
m = 16  -> alpha_m = 0.673
m = 32  -> alpha_m = 0.697
m = 64  -> alpha_m = 0.709
其他    -> alpha_m = 0.7213 / (1 + 1.079 / m)
```

小基数时，很多 register 仍为 0。设 0 register 的数量为 `V`，如果 `E <= 2.5m` 且 `V > 0`，使用 small-range correction：

```text
E_small = m * ln(m / V)
```

最终使用四舍五入到最近整数的结果，可以直接使用 `std::llround`。本项目的数据不会进入需要 large-range correction 的范围。

HLL 的典型相对标准误差约为 `1.04 / sqrt(m)`。因此更大的 `p` 通常精度更高，但需要更多 registers。

### 2.4 HLL 的合并

两个使用相同 `p` 和哈希函数的 HLL 可以直接合并。对每个 register 取最大值：

```text
merged[i] = max(left[i], right[i])
```

合并得到的状态近似表示两个集合的并集。`merge(target, source)` 只能修改 `target`，不能修改 `source`。

### 2.5 固定哈希函数

项目统一使用 SplitMix64。输入和所有中间结果均为 `uint64_t`，按照 64 位无符号整数自然溢出：

```text
x += 0x9e3779b97f4a7c15
x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9
x = (x ^ (x >> 27)) * 0x94d049bb133111eb
x = x ^ (x >> 31)
```

---

# 3. Basic：在 OJ 上实现 HLL 主体

## 3.1 任务目标

OJ 会提供完整的单文件程序模板和 `main`。你只需要完成 `HyperLogLog` 类中的核心内容：

1. SplitMix64；
2. register 下标计算；
3. `rho` 计算；
4. `add`；
5. 基本估计与 small-range correction；
6. `merge`。

不需要编写命令解释器，不需要使用字符串名称管理统计器，也不需要处理非法输入。

## 3.2 输入格式

第一行包含：

```text
p counter_count operation_count
```

随后有 `operation_count` 行，每行是一种操作：

```text
1 counter value
2 counter
3 target source
```

- `1 counter value`：向编号为 `counter` 的 HLL 加入 `value`；
- `2 counter`：查询该 HLL 当前估计的不同元素数量；
- `3 target source`：把 `source` 合并到 `target`，`source` 不得改变。

所有统计器使用同一个 `p`，编号范围为 `[0, counter_count-1]`。

## 3.3 输出格式

每次操作 `2` 输出一行非负整数。其他操作不产生输出。

## 3.4 数据范围

- `10 <= p <= 16`；
- `1 <= counter_count <= 4`；
- 单个测试点最多约 1,400,000 次操作；
- `value` 是任意 `uint64_t`；
- 输入包含空集合、重复元素、不同加入顺序、集合交叠和多次 merge；
- 推荐限制：4 秒、32 MiB，最终时间限制以课程 OJ 实测为准。

## 3.5 Special Judge 规则

答案文件保存每次查询的真实基数。Special Judge 不要求估计值与真实值完全相等，而是检查误差是否处于合理范围。

对较大基数，允许相对误差为：

```text
max(2%, 3.25 * 1.04 / sqrt(2^p))
```

真实基数为 0 时必须输出 0；真实基数不超过 32 时允许绝对误差 1；不超过 64 时允许绝对误差 2。输出行数必须正确，且不得包含额外内容。

OJ 共设置 10 个测试点，规模从几个操作逐步增加到百万级操作。较大的隐藏测试和内存限制会阻止永久保存全部用户 ID 的做法。

---

# 4. Hard：最近若干时间桶中的不同用户

## 4.1 任务目标

Basic 统计的是一个 HLL 从创建至今见过的所有不同元素。Hard 需要回答：

> 最近 `w` 个时间桶中，一共出现过多少个不同用户？

Hard 只保留这一主体问题：按时间桶组织 HLL，并在查询时合并窗口中的桶。不设置排行榜，不要求学生选择切换阈值，也不要求实现“精确集合转 HLL”的自适应结构。

所有时间桶统一使用 `p = 12`。

## 4.2 为什么按时间分桶

普通 HLL 可以加入元素，却不能可靠删除单个元素。如果某个 register 的最大值来自已经过期的用户，仅凭当前 register 无法知道删除后应恢复成什么值。

解决方法是让每个时间桶拥有独立的 HLL：

- `ADD t id` 时，只更新时间桶 `t`；
- `QUERY t w` 时，新建一个空 HLL，并合并闭区间 `[t-w+1, t]` 内的桶；
- 一个桶永久离开所有合法窗口后，可以整体删除。

这里没有让 HLL 支持删除单个用户，而是把删除旧数据转化为丢弃整个过期桶。

不能把各桶的估计值直接相加，因为同一个用户可能出现在多个桶中。必须合并 HLL 状态后再估计并集。

## 4.3 输入输出协议

程序从标准输入读取：

```text
ADD time user_id
QUERY time window
QUIT
```

- `ADD t id`：用户 `id` 在时间桶 `t` 出现一次；
- `QUERY t w`：输出 `[t-w+1, t]` 中不同用户数量的 HLL 估计；
- `QUIT`：结束程序。

所有命令中的 `time` 非递减。`1 <= window <= 256`。如果 `window > t+1`，窗口从时间 0 开始。只有 `QUERY` 输出一行整数。

## 4.4 建议实现结构

```text
WindowCounter
  ├── deque/map<time, HyperLogLog>
  ├── add(time, user_id)
  ├── query(time, window)
  └── expireOldBuckets(current_time)
```

每个桶直接使用 Basic 中实现的 HLL。查询时合并窗口范围内的 HLL，最后输出合并结果的估计值。

## 4.5 数据范围与完成标准

- `0 <= time <= 10^9`，时间非递减；
- `1 <= window <= 256`；
- 最多 4096 个非空时间桶；
- `ADD` 总数不超过 1,000,000；
- `QUERY` 总数不超过 1024；
- 用户 ID 为任意 `uint64_t`；
- 输入会包含桶内重复、跨桶重复、稀疏时间和过期数据。

完成 Hard 需要：

1. 正确实现窗口边界 `[t-w+1, t]`；
2. 通过合并 HLL 计算跨桶并集，而不是把估计值相加；
3. 及时清理不可能再进入合法窗口的旧桶；
4. 在公开数据中表现出与 `p=12` 的 HLL 相符的近似误差；
5. 不再进行排行榜评分。

把 Hard 源码放在 `student/hard/` 下，然后在 `student/` 目录运行：

```bash
python3 run_tests.py hard
python3 run_tests.py hard --stress
```

测试脚本使用 `g++ -std=c++17 -O2` 编译 `hard/` 中除 `tests/` 外的所有 `.cpp` 文件。Basic 的测试、判定和提交全部在 OJ 中完成，不再使用这个本地脚本。

---

## 5. 常见错误

- register 下标和 `rho` 使用了同一批哈希位；
- `rho` 从整个 64 位哈希开始计算，没有排除最高 `p` 位；
- register 使用累加而不是取最大值；
- 忘记 small-range correction；
- merge 时把 registers 相加；
- Hard 中把每个桶的估计值直接求和；
- Hard 的窗口左端点写成 `t-w`，正确值应为 `t-w+1`；
- 没有清理已经永久过期的时间桶。

## 6. 参考阅读
https://zhuanlan.zhihu.com/p/1944936956199962569
https://zhuanlan.zhihu.com/p/77289303更详细但较难
https://zhuanlan.zhihu.com/p/58519480