# 可靠传输 · Advance

先完成 [Basic](../basic/README.md)。本阶段的具体目标和验收以 [完整任务书](../README.md) 为主。

## 项目结构与材料定位

- [../basic/materials/src/main.cpp](../basic/materials/src/main.cpp)：Basic 停止等待实现起点。
- [../basic/materials/public-tests/](../basic/materials/public-tests/)：Basic 公开样例。
- [../README.md](../README.md)：完整 Advance 的 G1–G6、GBN 窗口、延迟/重复规则与实验要求。

## 建议阅读与使用顺序

1. 先让 Basic 的 W=1 行为和日志完全可复现，再读完整任务书 Advance。
2. 扩展网络事件为丢失、延迟、重复，随后加入 GBN 的 base、next、窗口和单计时器。
3. 固定消息和异常配置，比较 W=1/2/4、超时阈值与乱序场景。
4. 记录发送、重传、ACK、完成时刻和失败案例；最终报告解释模型边界。

## 本地起步

从项目根目录运行：

    cmake -S basic/materials -B build
    cmake --build build

目前提供的是 Basic 框架，Advance 的 GBN 代码需要在自己的项目中实现。
