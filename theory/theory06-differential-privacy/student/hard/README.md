# Differential Privacy & Sparse Vector Project

## 1. 题目背景

课程平台经常需要发布人数、总分或“哪些知识点反馈较多”等统计结果。直接发布精确结果可能泄露个人信息：如果攻击者知道除一人之外的全部数据，就可能通过结果推断最后一人的记录。

差分隐私（Differential Privacy, DP）通过向统计结果加入经过校准的随机噪声，降低单个用户是否出现在数据集中对输出的影响。本项目关注三个核心概念：

- **Sensitivity**：一名用户最多能让真实答案改变多少。
- **Laplace Mechanism**：发布 `truth + Laplace(sensitivity / epsilon)`。
- **Privacy budget**：多次访问同一数据集会不断消耗 epsilon。

项目包含两个相互独立的任务，完成其中一个即可：

- **Basic**：非常简单的带隐私预算的匿名统计发布器，只需要完成少量计算
- **Hard**：课程反馈告警系统，对比逐个发布的 NAIVE 方法与 Sparse Vector 的 ALERT 方法。

Hard 不要求先完成 Basic。hard提供 `starter.cpp`；开始时把它复制为同目录的 `main.cpp`，只填写 TODO，不要修改题目提供的随机采样函数。

---

## 2. Basic：匿名统计发布器

请看OJ，完成即可，你应当阅读最后给出的文章或自行搜索，了解方法原理后开始工作。（不过好心的助教已经实际说明了你要做什么

## 3. Hard：课程反馈告警系统

### 3.1 题目背景

每条事件是：

```text
student_id topic_id
```

表示某名学生反馈了一个困难知识点。同一学生对同一 topic 重复点击，只能计数一次。因此 `topicCount(topic)` 是反馈该 topic 的不同学生人数，每个 topic 查询的 sensitivity 为 1。

本题只要求实现两种模式：`NAIVE` 和 `ALERT`。

### 3.2 NAIVE

把总 epsilon 平均分给全部 query：

```text
epsilon_each = epsilon / query_count
noisy_count = true_count + Laplace(1 / epsilon_each)
```

如果 noisy count 大于等于 threshold，输出 ALERT，否则输出 BELOW。

### 3.3 ALERT

实现最多返回 `max_hits` 个 positive answer 的 Sparse Vector：

```text
sigma = 2 * max_hits / epsilon
noisy_threshold = threshold + Laplace(sigma)
noisy_query = true_count + Laplace(2 * sigma)
```

按输入顺序检查 topic：

1. noisy query 小于 noisy threshold，输出 BELOW；
2. 否则输出 ALERT，并增加 hits；
3. 命中但尚未达到 `max_hits` 时，重新采样 noisy threshold；
4. 达到 `max_hits` 后，剩余位置全部输出 FINISHED。

FIRST 不再作为独立模式；它可以视为 `max_hits = 1` 的 ALERT。NUMERIC 不属于必做范围。

### 3.4 Hard 输入格式

```text
event_count seed
student_id topic_id       # 共 event_count 行
mode threshold max_hits epsilon
query_count
topic_1 topic_2 ...
```

`mode` 只可能是 `NAIVE` 或 `ALERT`。

范围：

```text
0 <= event_count <= 300000
1 <= query_count <= 5000
1 <= max_hits <= min(100, query_count)
0 < epsilon <= 10^6
```

student id 和 topic id 不保证连续。

### 3.5 Hard 输出格式

每个 query 位置输出一行，总行数必须等于 `query_count`：

```text
BELOW topic_id
ALERT topic_id
FINISHED
```

### 3.6 Hard 实现指引

推荐按以下顺序完成：

1. 使用 `topic -> set of students` 完成重复贡献去重；
2. 实现并用大 epsilon 测试 NAIVE；
3. 保存 `noisy_threshold`、`hits` 和 finished 状态；
4. 实现 ALERT 的逐项查询和阈值刷新；
5. 最后检查达到 `max_hits` 后是否仍为剩余位置输出 FINISHED。

这里的贡献限制是“同一学生对同一 topic 最多贡献 1”。本项目不进一步限制一名学生可以反馈多少个不同 topic。

本地运行：

```bash
python3 run_tests.py hard
python3 run_tests.py hard --stress
```

---

## 4. 编译与文件要求

推荐环境：Python 3.9+、支持 C++17 的 g++。

评测入口必须是：

```text
hard/main.cpp
```

测试器使用类似下面的命令：

```bash
g++ -std=c++17 -O2 basic/main.cpp -I basic -o .build/basic
```

## 5.参考阅读

https://zhuanlan.zhihu.com/p/139114240
https://blog.csdn.net/Kenji_Shinji/article/details/126720793

下面这篇文章更详尽，但较为困难，有兴趣的同学可以阅读
https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf
