# LSH 近似最近邻检索（基础版 · 学生版）

> 一句话：用 **E2LSH（欧氏距离）** 在一张表里把候选缩小，再用真实距离重排，单文件 Python/NumPy。**三个核心函数留 TODO，你来写**，写完用 Q5 手算核对。

对应 `../project8-基于LSH的近似最近邻检索.md` 的 **Basic** 部分。project8 第 3 节明确说 `build_index / query / brute_force` 是"作业设计，不是已存在的 Python 文件"——所以本文件**不提供**这三个函数的实现，只有 TODO + 提示 + 注释里的参考答案。

## 这是个啥？

给定一堆向量，怎么快速找到和查询最相似的几个？最朴素的做法是逐个算距离（暴力搜索），数据一大就慢。**LSH（局部敏感哈希）** 的思路：让相近向量更可能落进同一个"桶"，查询时只在这些桶里找候选，再用真实距离精确重排。

基础版只建**一张表**，重点是把这套流程跑通、和暴力搜索对照、看漏检是怎么发生的。

### 用的哈希（E2LSH，欧氏距离）

```
h(x) = floor( (a·x + b) / w )
a：各维独立标准高斯的随机投影向量
b：[0, w) 上的均匀偏移
w：桶宽（>0）
```

一张表可以用 k 个这样的哈希组成元组当键（Basic 取 k=1 或 2）。

## 学完你能会啥？

- 分清"精确"与"近似"最近邻，知道用 Recall 衡量漏检
- 理解 E2LSH 的投影 + 分桶
- 自己实现暴力 top-K 和单表 LSH 查询
- 解释为什么桶内还要算真实距离、为什么会有漏检
- 核对 Q5 的手算例子

## 你需要准备

- Python 3.8+（项目用 3.12 测过）
- NumPy：`pip install numpy`

## 三步跑起来

```bash
cd basic

# 0. 直接跑（还没实现 TODO）→ 会抛 NotImplementedError，正常
python3 lsh_basic.py --handcalc

# 1. 打开 lsh_basic.py，实现 TODO 1/2/3（见函数注释提示）
#    卡住了取消注释里的参考答案看一眼，但建议先自己想

# 2. 实现后再跑 —— Q5 手算核对（project8 第 4 节，必看）
python3 lsh_basic.py --handcalc

# 3. 合成数据演示（500 个 2 维向量，k=1，w=2）
python3 lsh_basic.py
```

### 实现完 TODO 后，你应该看到（`--handcalc`）

```
Q5 手算核对：q = 1.9, h(x) = floor(x / 2)  (a=1, b=0, w=2)
  ID      x     桶号       到q距离       同桶候选
   a    0.2   (0,)        1.7          是
   b    1.0   (0,)        0.9          是
   c    2.1   (1,)        0.2          否
   d    4.5   (2,)        2.6          否

查询 q 的桶号: (0,)  → 同桶候选 ID: ['a', 'b']
暴力 top-1: c (距离 0.2)  ← 真实最近邻
LSH  top-1: b (距离 0.9)  ← 同桶最近邻
Recall@1 = 0  (漏检：c 没进候选，精确重排无法找回)
```

这是近似检索的**正常失败**：真实最近邻 c 落在隔壁桶，没进候选，精确重排也救不回来。代码没有硬编码补回答案。

## 项目结构

```
basic/
├── lsh_basic.py               ← 学生版（你要改的）：3 个函数是 TODO
└── solution/
    └── lsh_basic_complete.py  ← 参考答案（助教用 / 核对用），别直接抄
```

`lsh_basic.py` 分三块（注释里有分隔）：

1. **三个 TODO 函数**（`build_index` / `query` / `brute_force`）—— 你要实现的
2. **脚手架**（`_build_fixed_index` / `run_handcalc` / `run_demo`）—— 已实现，不用改，会调用你的 TODO 函数
3. **命令行**（`main`）—— 已实现

## 你要做的任务

### TODO 1：`build_index(vectors, k, w, seed)` —— 建一张 E2LSH 表

生成随机投影 A、偏移 B；对每个向量算键 `floor((a·x+b)/w)`；建桶字典。返回约定的 index dict（结构见文件顶部注释）。

**关键检查**：所有桶里 ID 加起来 = N（库大小）。

### TODO 2：`query(index, query_vector, top_k)` —— 同桶候选 + 真实距离重排

算查询键、查桶、算欧氏距离、按 `(距离, id)` 排序取前 top_k。空桶返回 `[]`，候选不足返回实际数量。

### TODO 3：`brute_force(vectors, query_vector, top_k)` —— 全库精确 top-K

对全库算欧氏距离，按 `(距离, id)` 排序取前 top_k。这是 Recall 的标准答案。

### 验收约定（project8，必须遵守）

- 空桶返回 `[]`；候选不足 `top_k` 返回实际数量，**绝不偷偷全库扫描**
- 同距离按 ID 升序固定排序
- `floor` 对负数向下取整：`floor(-0.1) = -1`，不能用 `int()` 向零截断
- 固定种子时键可复现

## 卡住了看这里

### 还没实现就跑，报 `NotImplementedError`

正常。这是设计内的"未完成"状态，不会崩溃。实现 TODO 后就能跑。

### `ModuleNotFoundError: No module named 'numpy'`

```bash
pip install numpy
```

### `Recall@1 = 0` 是不是写错了？

不是。Q5 的设计就是让你看到漏检——真实最近邻 c 被分到隔壁桶，单表 LSH 找不回来。这正是 Basic 想让你体会的"近似检索的正常失败"。

### 实在想不出来

打开 `solution/lsh_basic_complete.py` 看参考答案，或者直接跑它对比输出：

```bash
python3 solution/lsh_basic_complete.py --handcalc
```

但**学生提交版本必须是 `lsh_basic.py`（带 TODO 的那份）**，不是 solution。

## Q1–Q5（project8 文档要求提交）

实现完后跑 `--handcalc` 直接给出 Q5 的桶号与真实距离。Q1–Q4 是理解性问题，对照 `--handcalc` 和 `run_demo` 的输出作答：

| 编号 | 问题 | 回答应包含 |
| --- | --- | --- |
| Q1 | 精确 vs 近似最近邻 | 近似可能漏掉全局近邻，用召回衡量漏检 |
| Q2 | LSH 与普通哈希目标 | 相似点希望高概率碰撞，不指望所有不同点分开 |
| Q3 | 桶内为何还要算真实距离 | 同桶不保证近；精确重排只保证候选内部次序 |
| Q4 | Recall@K 与分类准确率 | 前者看找回多少真实近邻 ID，后者看类别是否相同 |
| Q5 | h(x)=floor(x/2)，q=1.9 | 见 `--handcalc` 输出，Recall@1=0 |

## 想再挑战？

跑通基础版后，去 `../advanced/` 看提高版：多表 LSH、参数扫描、Recall@10/延迟/内存测量、召回-延迟折中曲线。

## 自查清单

- [ ] 实现了 TODO 1/2/3，`--handcalc` 不再报 NotImplementedError
- [ ] `--handcalc` 输出和 Q5 表格一致，Recall@1=0
- [ ] 合成数据演示能跑，桶中 ID 总数 = N
- [ ] 改 `--k 2` 后候选数明显下降
- [ ] 能解释为什么 c 没进候选
- [ ] Q1–Q5 都能答
