# Bloom Filter 算法与应用

## 项目入口

- [Basic 学生任务](basic/README.md)
- [Advance 学生任务](advance/README.md)

## A 问题是什么

当集合很大时，能否用很少的空间快速判断一个元素是否出现过？Bloom Filter 用位数组记录多个哈希位置，查询时可以给出“一定不存在”或“可能存在”。它用允许假阳性换取空间，而不是保存完整元素。Basic 实现最小插入与查询；Advance 加入位压缩、参数实验和一个应用模拟，理解近似数据结构在数据库、缓存与去重中的用途。

| 阶段 | 工作量 | 难度 | 主要成果 |
| --- | --- | --- | --- |
| Basic | 一周约 10–20 小时 | easy | 用数组实现插入、查询，观察假阳性 |
| Advance | Basic 后追加六周 | medium | 位数组实现、误判实验及黑名单预筛 |

C++11 即可，需要数组、字符串与循环。easy 为明确步骤的局部任务，medium 需要实验设计或组合机制，hard 需要理解更复杂的数据结构。Basic 可用一个字节模拟一个位；真正的位压缩放到 Advance。

项目中的代码位于 `advance/`。学生需要完成 `experiment/src.hpp` 和 `application/application.hpp`。

### Basic：可能存在与一定不存在

#### 1 需要回答的问题

| 编号 | 问题 | 回答要求 |
| --- | --- | --- |
| Q1 | 成员查询与统计元素数量有什么区别？ | 分别举例，说明 Bloom Filter 回答哪一种问题 |
| Q2 | 位数组和哈希函数如何共同完成插入、查询？ | 描述设置哪些位置、查询时检查什么 |
| Q3 | 假阳性是什么？标准 Bloom Filter 为什么不会漏掉已插入元素？ | 用两个字符串共用位置解释；前提是只插入、哈希规则一致、位没有被清除 |
| Q4 | 为什么不能删除元素时直接把它对应的位清零？ | 用共享位置说明可能造成假阴性 |
| Q5 | 按下文 m=8 的规则插入 `a`，再查 `a`、`i`、`b`，结果分别是什么？ | 手算哈希位置，指出哪一次是假阳性，不能把 MAYBE 当作确定存在 |

#### 2 代码任务

本任务对应 ACM Class OnlineJudge 题目 **3261**，以 OJ 上发布的题面和提交入口为准。

输入第一行为容量 m 与操作数 n，后面 n 行是 `add 字符串` 或 `query 字符串`。约定 `1 <= m <= 1000000`、`0 <= n <= 10000`，字符串是非空 ASCII 字符串且不含空白，长度不超过 100。

用 `vector<uint8_t>` 保存 m 个 0/1 值。为了便于手算，Basic 固定使用以下两个教学哈希，c_i 为第 i 个字节的无符号数值，i 从 1 开始：

```text
h1(s) = sum(c_i) mod m
h2(s) = sum(i * c_i) mod m
```

- `add(s)`：把 h1、h2 对应位置都设为 1，不输出内容。
- `query(s)`：任一位置为 0 则输出 `NO`，否则输出 `MAYBE`。
- 初始全部为 0；重复插入不改变已有的 1；不支持删除。

这两个哈希只用于看清算法规则，相关性较强，不用于宣称真实误判率满足理想公式。Basic 的 m 个字节也不能按 m 个物理比特报告空间。

```text
输入：
8 4
add a
query a
query i
query b

输出：
MAYBE
MAYBE
NO
```

`a` 与 `i` 的两个位置都为 1，因此没有插入过的 `i` 也被判为可能存在。再用 `std::set<string>` 保存真实集合，作为测试时的答案来源，不能用它代替 Bloom Filter 的查询。

#### 3 参考资料

先读 B1 的原理，再用 B2、B3 补齐映射与哈希概念；B4 为英文对照。资料无需全部阅读。

| 编号 | 资料与语言 | 建议范围 |
| --- | --- | --- |
| B1 | [Apache Doris：BloomFilter 索引，中文](https://doris.apache.org/zh-CN/docs/dev/table-design/index/bloomfilter) | 只读索引原理与可能存在／一定不存在，不要求安装数据库 |
| B2 | [Hello 算法：哈希表，中文](https://www.hello-algo.com/chapter_hashing/hash_map/) | 精确集合与映射的背景，理解测试基线 |
| B3 | [Hello 算法：哈希算法，中文](https://www.hello-algo.com/chapter_hashing/hash_algorithm/) | 哈希值、分布与碰撞，帮助解释 Q2–Q4 |
| B4 | [Redis：Bloom filter，英文](https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/) | 工作方式与 false positive，预览应用 |

#### 4 提交与验收

提交 OJ 3261 的 AC 记录、Q1–Q5 和测试记录。测试覆盖空集合、重复插入、不同字符串碰撞、m=1、查询不存在的字符串；所有已插入元素必须返回 MAYBE，不要求所有未插入元素返回 NO。

### Advance：空间、误判与应用

#### 1 Goals 与难度

G1–G6 均需完成；G4 固定实现黑名单预筛，G5 两个阅读方向选一个。详细输入输出和测试方法见 [advance/README.md](advance/README.md)。

| Goal | 完成要求 | 难度 |
| --- | --- | --- |
| G1 | 使用真正的位数组，支持参数 m、k，并采用更合适的哈希位置生成方式 | medium |
| G2 | 用精确集合验证无假阴性，测量假阳性率及存储大小 | easy |
| G3 | 改变元素数量、m 和 k，解释误判、空间与计算量之间的关系 | medium |
| G4 | 实现一个应用模拟，说明假阳性在业务里会造成什么结果 | medium |
| G5 | 选择一种扩展阅读并讲解 | 见方向表 |
| G6 | 整理源码，并现场说明参数实验、应用结果和选学方向 | medium |

#### 2 位数组与哈希

用 `vector<uint8_t>` 的每一位保存一个逻辑位：位置 i 对应字节 `i / 8`，位下标 `i % 8`，存储长度为 `(m + 7) / 8`。自己实现设置位、读取位、add 与 query，避免直接调用现成 Bloom Filter 库。

学生版附有 [哈希辅助文件](advance/experiment/hash.hpp) 和 [内存代理](advance/experiment/memory.hpp)。可调用 `hash64(s)` 和 `splitmix64`，第 i 个位置定义为：

```text
splitmix64(hash64(s) + uint64_t(i) * 0x9e3779b97f4a7c15ULL) % m
```

i 从 0 到 k−1，整数运算采用 `uint64_t` 的回绕规则。建议测试 `1 <= k <= 8`，并记录参数。哈希辅助代码允许直接使用；同一过滤器的插入与查询必须采用完全相同的规则。学生通过 `Memory::read` 和 `Memory::write` 操作字节，`Memory::size` 给出实际申请的字节数。该生成方法仍不意味着严格独立的随机哈希，误判率需要实验检验。

#### 3 实验怎么做

先生成并插入 n 个互不相同的字符串，再用另一组**确认未插入**的字符串查询。借助 `set` 核对标签：

```text
假阳性率 = 未插入的测试字符串中返回 MAYBE 的个数 / 未插入的测试字符串总数
```

另外检查所有已插入元素，假阴性数必须为 0。查询集非空；不要用所有查询次数作假阳性率分母。固定随机种子并保存生成规则。

至少比较三种每元素位数（如 4、8、12）与三种 k，在同一批插入／查询数据上比较；再增加插入量观察位数组趋于饱和。理想独立均匀哈希模型下，常用近似为 `p ≈ (1 - exp(-k*n/m))^k`，可作趋势参考，不要求推导或逐点吻合。k 增加并不一定更好。[Redis 的容量与误判说明](https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/)

报告位数组实际字节数；与精确集合比较时分别说明元素内容大小和容器开销的统计口径，不能把 `(m+7)/8` 与整个 `set` 进程内存混为同一指标。

#### 4 G4 黑名单预筛

输入一份虚拟邮箱黑名单和待查地址。NO 直接放行，MAYBE 再查精确黑名单，统计减少了多少次精确查询；最终判定须与精确基线一致。解释为什么不能仅凭 MAYBE 封禁。下发测试会检查最终判断和精确查询次数。

#### 5 参考资料与可选方向

| 编号 | 资料与语言 | 建议范围 |
| --- | --- | --- |
| A1 | [Apache Doris：BloomFilter 索引，中文](https://doris.apache.org/zh-CN/docs/dev/table-design/index/bloomfilter) | 为什么可跳过某些数据块，怎样避免把假阳性变成错误答案 |
| A2 | [Hello 算法：哈希算法，中文](https://www.hello-algo.com/chapter_hashing/hash_algorithm/) | 分布、碰撞与哈希代价，支持 G1、G3 |
| A3 | [Redis：Bloom filter，英文](https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/) | 参数、误判与应用；不要求部署 Redis |
| A4 | [Bloom 1970 原论文入口，英文](https://doi.org/10.1145/362686.362692) | 选读摘要与空间—时间—错误率取舍，全文若不可访问可用 A1、A3 完成目标 |
| A5 | [Redis：Cuckoo filter，英文](https://redis.io/docs/latest/develop/data-types/probabilistic/cuckoo-filter/) | 选读成员查询、删除及与 Bloom Filter 的区别 |

| G5 可选方向 | 难度 | 需要回答的问题 |
| --- | --- | --- |
| 数据库与缓存中的预筛（A1、A3） | medium | 为什么“一定不存在”可以节省查询，而“可能存在”还需要核对？ |
| 支持删除的过滤器（A5） | hard | Cuckoo Filter 怎样保存指纹并支持删除？它与直接清空 Bloom 位的区别是什么？ |

选学只需阅读和讲解。最终提交实验与应用源码，并现场说明参数实验和应用结果。

学生版构建与测试：

```sh
cmake -S advance -B build-advance
cmake --build build-advance
ctest --test-dir build-advance --output-on-failure
```

## B 工作量安排与 Checkpoint

### Basic：一周

| 内容 | 预计用时 |
| --- | --- |
| 理解位数组、哈希与误判 | 3–4 小时 |
| 实现两种教学哈希与插入查询 | 3–5 小时 |
| 精确基线、手算和边界测试 | 2–4 小时 |
| Q1–Q5 与整理 | 2–3 小时 |
| 合计 | 10–16 小时，预留至 20 小时 |

Checkpoint：通过样例，能展示一个假阳性并解释为什么已插入元素不会被漏掉。

### Advance：追加六周

| 时间 | 对应 Goal | Checkpoint |
| --- | --- | --- |
| 第 1–2 周 | G1：medium；G2：easy | 位数组实现正确，与精确集合核对，无假阴性 |
| 第 3–4 周 | G3、G4：medium | 完成参数实验和一个应用模拟，正确解释误判的后果 |
| 第 5–6 周 | G5：按方向；G6：medium | 补齐阅读、测试与展示，说明适用场景和局限 |

## C 问题的来龙去脉与发展过程

1970 年，Burton Bloom 提出用允许少量判定错误换取存储和查询效率的方法。位数组记录的是元素经过哈希后的痕迹，因此节省了保存完整元素的空间，也使不同元素可能无法区分。[Bloom 原论文](https://doi.org/10.1145/362686.362692)

这类结构后来进入数据库索引、缓存和网络应用。在数据库预筛中，假阳性通常只导致多做一次精确检查；在近似爬虫去重中，它却可能使页面被跳过。同一个算法是否合适，取决于系统能否承受这种误差。支持删除等需求又推动了其他过滤器设计。[Apache Doris](https://doris.apache.org/zh-CN/docs/dev/table-design/index/bloomfilter)、[Redis Cuckoo Filter](https://redis.io/docs/latest/develop/data-types/probabilistic/cuckoo-filter/)
