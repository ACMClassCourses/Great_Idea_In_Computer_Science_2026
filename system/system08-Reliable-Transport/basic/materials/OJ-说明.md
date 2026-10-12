# Basic：停止等待可靠传输模拟器

## 题目描述

在一个 C++17 程序中模拟发送方、接收方和不可靠网络。发送方使用序号、累计确认和超时重传，在可能丢包的网络上把消息按顺序且不重复地交付给接收方。

- `DATA(i, content)` 是序号为 `i` 的完整消息。
- `ACK(k)` 表示接收方已经交付所有序号小于 `k` 的消息，下一条期待 `k`。
- 数据包和 ACK 的正常单程延迟都是 1。
- 每个时刻先按事件加入顺序处理全部到达事件，再判断超时。
- 首次发送或重传后，如果在 `当前时刻 + RTO` 仍未获得有效确认，则重传当前数据并重新计时。
- 接收方只在 `i == expected` 时交付消息并增加 `expected`；收到重复或非预期数据时不交付，但仍回复当前 `ACK(expected)`。
- 发送方仅在收到当前数据 `i` 的 `ACK(i+1)` 后前进，并立即发送下一条；旧确认和无效确认不得推进状态或重置计时器。
- 发送次数按包类型和编号分别从 1 开始计数，被丢弃的发送也计数。

## 输入格式

第一行一个整数 `T`，表示模拟数量。每组模拟格式如下：

```text
N RTO max_tick L
message_0 message_1 ... message_(N-1)
type id attempt
... 共 L 行
```

`N` 为消息数。消息均为不含空白的非空字符串；`N=0` 时没有消息。`RTO` 为正整数，`max_tick` 为非负整数。

每条丢包规则由包类型 `DATA` 或 `ACK`、包编号 `id`、发送次数 `attempt` 组成。`DATA` 的编号是消息序号；`ACK` 的编号是累计确认值。每个三元组至多出现一次，输入保证合法。

## 输出格式

你可以输出事件日志，但每条日志必须单独成行并以 `LOG ` 开头。每组模拟最终输出恰好一行：

```text
RESULT status finish_tick delivered_count data_sends retransmissions ack_sends dropped_count [delivered messages...]
```

- `status` 是 `SUCCESS` 或 `INCOMPLETE`。
- 发送方确认全部消息时立即成功，`finish_tick` 为该时刻；处理完 `max_tick` 仍未完成时，状态为 `INCOMPLETE` 且 `finish_tick=-1`。
- `data_sends` 包含首次发送和重传；`retransmissions` 只统计同一数据编号首次发送之后的发送。
- `ack_sends` 包含被丢弃的 ACK；`dropped_count` 统计所有被规则丢弃的 DATA 与 ACK。
- 最后按顺序列出接收方已经交付的消息，数量必须等于 `delivered_count`。
- 空消息列表在时刻 0 成功。

SPJ 会忽略合法的 `LOG ` 行，并严格核对每一行 `RESULT` 的字段。

## 样例

输入：

```text
3
3 4 100 0
A B C
3 4 100 1
A B C
ACK 2 1
0 4 0 0
```

输出（省略可选日志）：

```text
RESULT SUCCESS 6 3 3 0 3 0 A B C
RESULT SUCCESS 10 3 4 1 4 1 A B C
RESULT SUCCESS 0 0 0 0 0 0
```

第二组在时刻 3 丢弃第一次发送的 `ACK(2)`。发送方在时刻 6 超时并重传 `DATA(1, B)`；接收方不重复交付 B，但再次回复 `ACK(2)`，最终在时刻 10 完成。

## 数据范围

- `1 <= T <= 30`
- `0 <= N <= 100`
- `1 <= RTO <= 1000`
- `0 <= max_tick <= 100000`
- 所有消息总长度不超过 10000
- `0 <= L <= 1000`

时间限制：1 秒；内存限制：256 MiB。

课程 Basic 的完整交付还包括 Q1–Q5、数据包与 ACK 丢失的时间线、运行说明和至少六组测试记录；本题只自动验收模拟器。
