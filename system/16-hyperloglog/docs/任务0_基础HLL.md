# 任务 0：基础 HLL

对应文件：

```text
part0_naive.hpp
```

这一阶段先不做压缩存储。

每个寄存器直接用一个 `uint8_t` 保存。

目标是先把 HLL 的算法逻辑写正确。

## 接口对照

| 小问 | 要解决的问题 | 需要完成的接口 |
| --- | --- | --- |
| 1 | 一个元素怎样更新一个寄存器 | `HLL0::add` |
| 2 | 怎样从寄存器得到基数估计 | `HLL0::estimate` |
| 3 | 两个 HLL 怎样合并 | `HLL0::merge` |

## 小问 1：add

接口：

```cpp
void add(const std::string& value);
```

需要完成 4 步：

1. 调用 `hash64(value)` 得到 64 位哈希值。
2. 调用 `bucketIndex(hash, p_)` 得到桶号。
3. 调用 `rho(hash, p_)` 得到当前元素的 rank。
4. 用较大值更新对应寄存器。

更新规则：

```text
registers_[index] = max(registers_[index], rank)
```

重复加入同一个元素不应继续增大寄存器。

## 小问 2：estimate

接口：

```cpp
double estimate() const;
```

先计算：

```text
Z = sum(2^(-M[j]))
```

原始估计值：

```text
E = alpha_m * m^2 / Z
```

`alpha_m` 可以调用 `hllAlpha(m_)`。

然后统计值为 0 的寄存器数量 `V`。

当估计值较小，并且 `V > 0` 时，使用线性计数修正：

```text
E = m * log(m / V)
```

这里最重要的是把公式和每个变量对应起来。

## 小问 3：merge

接口：

```cpp
void merge(const HLL0& other);
```

两个 HLL 的 `p` 必须相同。

合并时逐个寄存器取最大值：

```text
M[i] = max(M[i], other.M[i])
```

不要把两个估计值直接相加。

## 第 2 周检查

需要完成 3 个小问。

需要能解释：

- 桶号来自哈希值的哪一部分。
- `rho` 表示什么。
- 为什么寄存器只保留最大值。
- 为什么 merge 是逐桶取最大值。
