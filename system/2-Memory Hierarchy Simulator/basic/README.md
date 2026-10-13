# Basic：FIFO Cache Simulator

## 要做什么

完成 ACM Class OnlineJudge 题目 **3275. FIFO Cache Simulator**。程序按 FIFO 策略处理访问序列，并输出 cache miss 次数。

请先阅读根目录 `README.md` 中的 Basic 部分并完成 Q1–Q5。Basic 不提供代码模板，请自行创建一个完整的 `main.cpp`，实现输入、FIFO 模拟和答案输出。

## 输入与输出

第一行是两个正整数 `c n`，分别表示缓存容量和访问次数；第二行是 `n` 个 `int` 范围内的非负整数。

```text
3 7
1 2 3 1 4 2 5
```

程序只输出一行 cache miss 次数：

```text
5
```

数据范围为 `1 <= c, n <= 100`。提交 OJ 时不要输出提示语、缓存状态或其他调试信息。

## 完成标准

- 独立完成一份可提交到 OJ 的 `main.cpp`，FIFO 命中时不改变原有顺序。
- 样例输出为 `5`，并检查容量为 1、连续重复访问和所有对象都能装入的情况。
- 将 `main.cpp` 提交到 OJ 3275 并获得 Accepted。
- 提交 Q1–Q5 的回答和 OJ AC 记录。
