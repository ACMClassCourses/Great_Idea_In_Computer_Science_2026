# 支持向量机与群智能算法优化 · Advance

先完成 [Basic](../basic/README.md)。本阶段的具体目标和验收以 [完整任务书](../README.md) 为主。

## 项目结构与材料定位

- [src/svmswarm/](../src/svmswarm/)：数据、基线、评价、目标函数、PSO/GA 与可视化模块。
- [examples/README.md](../examples/README.md)：编号示例的用途；00_self_check.py 是接口自检，03/04 是实验入口。
- [iris.data](../iris.data) 与 [madelon/](../madelon/)：示例及 Advance 数据；outputs/ 保存生成结果。
- [requirements.txt](../requirements.txt)、[pyproject.toml](../pyproject.toml)：环境说明。

## 建议阅读与使用顺序

1. 先读根目录 Advance 的 G1–G7，固定相同的数据切分、CV 折和评价预算。
2. 读 examples/README.md，再按 00 → 01 → 02 → 03 → 04 的顺序理解自检、基础分类、测试函数和正式实验。
3. 在 Sphere 上验证 PSO 的边界、复现性和预算，再接入 RBF-SVM；不要用最终测试集调参。
4. 统一报告默认模型、随机搜索与 PSO 的指标、评价次数、耗时和失败案例。

## 本地起步

从项目根目录运行：

    python -m pip install -r requirements.txt
    python examples/00_self_check.py
    python examples/02_test_functions.py

公开自检只验证接口和基本性质，不提供 TODO 的参考实现。
