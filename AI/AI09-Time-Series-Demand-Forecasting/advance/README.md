# 时间序列需求预测 · Advance

先完成 [Basic](../basic/README.md)。本阶段的具体目标和验收以 [完整任务书](../README.md) 为主。

## 项目结构与材料定位

- [data/](../data/)：自行准备 UCI Bike Sharing 的 hour.csv；仓库不附数据。
- 根目录 README：完整 Advance 要求、时间切分与信息可得性约束。

## 建议阅读与使用顺序

1. 先复核 Basic 的时间戳对齐与严格向前预测，再阅读 Advance 的 G1–G7。
2. 建立特征可得时刻表，固定时间切分；新增一个模型和只用过去残差更新的预测区间。
3. 比较总体及分场景误差、覆盖率和区间宽度，并解释失效时段。

## 本地起步

代码入口在 [`src/ts9/`](../src/ts9/)：`ingest` 读入与时间审计、`baselines` 三个点预测基线、`metrics` 误差指标、`features` 特征可得性、`interval` 滚动残差区间、`evaluate` 分场景评价。按根目录 README 的 Basic / Advance 任务补全各模块的 TODO，可运行 [`examples/`](../examples/) 自检。
