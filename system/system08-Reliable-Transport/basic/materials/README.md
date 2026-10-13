# 可靠传输协议 Basic：停止等待模拟器

完成 `src/main.cpp` 中的 `simulate`。程序在一个进程内模拟发送方、接收方和不可靠网络，不使用 Socket、多线程或真实等待。

## 输入格式

第一行是模拟数量 `T`。每组模拟依次给出：

```text
N RTO max_tick L
message_0 message_1 ... message_(N-1)
type id attempt
... 共 L 条丢包规则
```

- `N` 是消息数，消息是不含空白的非空字符串；`N=0` 时消息行可省略。
- `RTO` 是正整数；`max_tick` 是非负整数。
- 每条规则的 `type` 为 `DATA` 或 `ACK`。
- `id` 是包编号：`DATA` 使用消息序号 `0..N-1`；`ACK(k)` 使用累计确认值 `k`。
- `attempt` 是该类型、该编号的第几次发送，从 1 开始；被丢弃的发送也计数。
- 同一个 `(type, id, attempt)` 最多出现一次。

输入保证符合这些约束。Basic 中未命中规则的包单程延迟恒为 1。

## 模拟顺序

时间从 0 开始。每个时刻先按事件加入顺序处理所有到达事件，再检查超时。发送或重传后，截止时刻为 `当前时刻 + RTO`；该时刻若尚无有效确认，就重传并重新计时。

- 接收方仅交付 `i == expected` 的数据；收到任何数据包都回复当前 `ACK(expected)`。
- 发送方只有收到当前数据 `i` 对应的 `ACK(i+1)` 才前进并立即发送下一条。
- 旧确认或无效确认不能推进状态，也不能重置计时器。
- 处理完 `max_tick` 时刻仍未全部确认，结果是 `INCOMPLETE`。
- 空消息列表在时刻 0 成功。

## 输出格式

可以输出任意数量的事件日志，每一行必须以 `LOG ` 开头。每组模拟最终必须输出恰好一行：

```text
RESULT status finish_tick delivered_count data_sends retransmissions ack_sends dropped_count [delivered messages...]
```

- `status` 为 `SUCCESS` 或 `INCOMPLETE`。
- 成功时 `finish_tick` 是发送方确认全部消息的时刻；未完成时为 `-1`。
- `dropped_count` 同时统计被规则丢弃的 DATA 和 ACK。
- 行末依次列出已经交付的消息，数量必须等于 `delivered_count`。

例如课程中的 ACK 丢失场景应输出：

```text
RESULT SUCCESS 10 3 4 1 4 1 A B C
```

## 本地运行

```sh
cmake -S . -B build
cmake --build build
./build/reliable_transport_basic < public-tests/1.in
```

将所有 `LOG ` 行移除后，结果应与 `public-tests/1.out` 一致。报告仍需完成 Q1–Q5、时间线和至少六组测试记录。
