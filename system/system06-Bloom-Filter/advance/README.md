# Advance 学生版

学生版包含参数实验和黑名单预筛应用。实验负责实现 Bloom Filter，应用负责正确使用它。

## 实验：实现 Bloom Filter

只修改 `experiment/src.hpp`，实现其中的 `BloomFilter` 类。其他文件均由课程提供，不需要修改：

- `memory.hpp`：负责申请、读取和写入字节，并报告实际字节数；
- `hash.hpp`：提供 `hash64` 和 `splitmix64`；
- `main.cpp`：生成固定实验数据并运行全部参数组合；
- `test.py`：检查参数组合、固定数据下的假阳性数量、假阴性和实际字节数。

`BloomFilter` 需要完成：

- 为 `m` 个逻辑位申请 `(m + 7) / 8` 字节；
- 设置和读取单个 bit；
- 按 README 的公式生成 `k` 个哈希位置；
- 实现 `add` 和 `contains`；
- 通过 `storage_bytes()` 返回内存代理实际申请的字节数。

不得使用额外容器保存已插入字符串或另一份位数组。Bloom Filter 的持久化状态必须保存在提供的 `Memory` 中。

## 构建与测试

```sh
cmake -S advance -B build-advance
cmake --build build-advance
ctest --test-dir build-advance --output-on-failure
```

CTest 默认隐藏成功测试的输出。查看完整实验表格可以使用：

```sh
ctest --test-dir build-advance -V
```

也可以在构建后直接运行测试脚本：

```sh
python3 advance/experiment/test.py build-advance/experiment/main
```

初始 `src.hpp` 可以编译，但测试不会通过。完成其中六处简短 TODO 后，测试应输出：

```text
PASS：存储、哈希、9 组参数实验和 4 组饱和实验均正确。
```

## 应用：黑名单预筛

只修改 `application/application.hpp`，完成其中一处 TODO。应用会直接复用实验中的 `BloomFilter`。

### 题目要求

你需要实现一个邮箱黑名单预筛器。系统同时维护：

- 完整邮箱地址黑名单；
- 域名黑名单；
- 可信邮箱地址白名单。

邮箱地址和域名中的英文字母不区分大小写。应用使用一个 Bloom Filter，将黑名单内容分别保存为：

```text
address:完整邮箱地址
domain:域名
```

Bloom Filter 固定使用以下参数：

```text
m = max(1, (地址黑名单数量 + 域名黑名单数量) * 8)
k = 4
```

对每个待查询邮箱，必须按以下顺序判断：

1. 如果完整邮箱位于可信白名单，直接判定为 `Not Spam`；
2. 否则分别用 Bloom Filter 查询完整邮箱和域名；
3. 两次查询都是 `false` 时，直接判定为 `Not Spam`；
4. 任意一次查询为 `true` 时，只调用一次 `ExactBlacklist::contains(email, domain)`；
5. 精确查询命中地址黑名单或域名黑名单时判定为 `Spam`，否则判定为 `Not Spam`。

Bloom Filter 只负责预筛。不能把 `MAYBE` 直接当作垃圾邮件，否则假阳性会造成错误封禁。

`ExactBlacklist` 私有保存精确地址和域名集合，并自动记录 `contains` 的调用次数。不要自行维护或输出查询次数，也不要另外保存一份精确黑名单。

### 输入格式

第一行输入三个非负整数 `A D T`，分别表示完整地址黑名单、域名黑名单和可信地址白名单的数量。

接下来的 `A` 行，每行输入一个黑名单邮箱地址。

接下来的 `D` 行，每行输入一个黑名单域名。

接下来的 `T` 行，每行输入一个可信邮箱地址。

随后一行输入非负整数 `Q`，表示待查询邮箱数量。

接下来的 `Q` 行，每行输入一个待查询邮箱地址。测试数据中的邮箱都恰好包含一个 `@`，并且 `@` 两侧均非空。

### 输出格式

对每个待查询邮箱输出一行：

- 最终位于地址黑名单或域名黑名单时输出 `Spam`；
- 否则输出 `Not Spam`。

处理完所有邮箱后，固定框架会再输出一行：

```text
Exact Queries: x
```

其中 `x` 是 `ExactBlacklist::contains` 的实际调用次数。一封邮箱即使地址和域名都返回 `MAYBE`，也只能计为一次精确查询。

### 样例

#### 输入

```text
0 1 1
badmail.com
Teacher@BadMail.com
3
visitor@BADMAIL.COM
teacher@badmail.com
friend@safe.org
```

#### 输出

```text
Spam
Not Spam
Not Spam
Exact Queries: 1
```

第一封邮件的域名在黑名单中，因此经过一次精确确认后输出 `Spam`。第二封邮件位于可信白名单，第三封邮件被 Bloom Filter 直接排除，因此二者都不增加精确查询次数。

### 需要完成的内容

在 `application/application.hpp` 的 `is_spam` 函数中实现上述单封邮件判断流程。输入、建表、大小写转换、域名提取和统计输出均已提供。

完成后的程序应满足：

- 所有最终判断都与精确黑名单一致；
- 可信邮件不进行精确查询；
- Bloom Filter 返回 `false` 时不进行精确查询；
- Bloom Filter 返回 `true` 时恰好进行一次精确查询。

### 测试应用

查看应用测试的中文统计表：

```sh
ctest --test-dir build-advance -V -R application
python3 advance/application/test.py \
  build-advance/application/bloom_application
```

学生骨架可以编译，但实验和应用测试都需要完成对应 TODO 后才能通过。
