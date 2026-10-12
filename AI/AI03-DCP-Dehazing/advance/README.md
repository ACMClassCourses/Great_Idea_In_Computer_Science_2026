# DCP 图像去雾 · Advance

先完成 [Basic](../basic/README.md)。本阶段的具体目标和验收以 [完整任务书](../README.md) 为主。

## 项目结构与材料定位

- [dehaze.py](../dehaze.py)：命令行入口。
- [src/dcp_dehaze/](../src/dcp_dehaze/)：暗通道、大气光、透射率、恢复及 I/O 模块；先看 pipeline.py，再按调用关系读各模块。
- [examples/](../examples/)：合成图演示和参数消融；[assets/](../assets/) 是输入材料说明，outputs/ 用于结果。
- [requirements.txt](../requirements.txt) 与 [pyproject.toml](../pyproject.toml)：依赖和项目配置。

## 建议阅读与使用顺序

1. 先完成 Basic 的粗透射率和恢复，保留可复现的基线。
2. 阅读根目录任务书 Advance 的 G1–G7，再看 pipeline.py 中 refine 开关和 transmission.py 的细化函数。
3. 用 run_demo.py 核对完整调用；自行准备有来源的真实图，在相同输入上比较细化开关与参数。
4. 记录合成图指标、真实图失败案例、耗时和种子；报告里分开描述数值改善与视觉观察。

## 本地起步

从项目根目录运行：

    python -m pip install -r requirements.txt
    python examples/run_demo.py
    python dehaze.py -i hazy.png -o outputs/advance
