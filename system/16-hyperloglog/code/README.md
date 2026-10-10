# 学生代码框架

这份代码只提供接口和必要的数据结构。

不要求自己设计类层次。

没有继承、虚函数或复杂模板。

建议只修改下面三个文件：

```text
part0_naive.hpp
part1_dense.hpp
part2_sparse.hpp
```

`hash.hpp` 已经提供，不需要修改。

## part0_naive.hpp

### HLL0::add

输入一个字符串。

需要：

```text
计算 hash
计算桶号
计算 rho
更新寄存器最大值
```

### HLL0::estimate

遍历所有寄存器。

需要：

```text
计算原始 HLL 估计
统计空桶
必要时做小基数修正
```

### HLL0::merge

把另一个 HLL 合并进当前对象。

需要：

```text
检查 p
每个寄存器取最大值
```

## part1_dense.hpp

### DenseHLL::get

读取第 `i` 个 6 位寄存器。

### DenseHLL::set

写入第 `i` 个 6 位寄存器。

不能影响相邻寄存器。

写入后缓存失效。

### DenseHLL::add

算法与 `HLL0::add` 相同。

寄存器通过 `get/set` 访问。

### DenseHLL::estimate

缓存有效时直接返回缓存。

缓存无效时重新计算。

### DenseHLL::invalidate

这个函数已经提供。

它只负责让缓存失效。

### DenseHLL::merge

逐寄存器取最大值。

### DenseHLL::dump

生成 16 字节头和 dense 正文。

缓存不用写进文件。

格式见 `../docs/任务1_密集存储.md`.

### DenseHLL::load

检查输入格式并恢复对象。

## part2_sparse.hpp

### SparseHLL::sparseBytes

计算当前 sparse 正文需要多少字节。

不需要真的生成正文。

### SparseHLL::updateEntry

更新一个非零寄存器。

`entries_` 必须始终按 `index` 递增。

### SparseHLL::add

当前是 sparse 时更新 `entries_`。

当前是 dense 时调用 `dense_data_`。

### SparseHLL::estimate

sparse 时根据非零项和空桶计算。

dense 时调用 `dense_data_.estimate()`。

### SparseHLL::merge

处理四种情况：

```text
dense + dense
dense + sparse
sparse + sparse
sparse + dense
```

### SparseHLL::promote

把所有 sparse entry 写入 DenseHLL。

转换前后逻辑寄存器不能变化。

### SparseHLL::dump

sparse 时使用 ZERO、XZERO、VAL。

dense 时直接使用 DenseHLL 的格式。

### SparseHLL::load

根据 `encoding` 判断要恢复 sparse 还是 dense。

## 推荐顺序

```text
HLL0::add
HLL0::estimate
HLL0::merge
DenseHLL::get
DenseHLL::set
DenseHLL::add
DenseHLL::estimate
DenseHLL::merge
DenseHLL::dump/load
SparseHLL::updateEntry
SparseHLL::add
SparseHLL::estimate
SparseHLL::sparseBytes
SparseHLL::promote
SparseHLL::merge
SparseHLL::dump/load
```
