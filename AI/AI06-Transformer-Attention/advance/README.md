# Transformer · Advance

先完成 [Basic](../basic/README.md)。本阶段的具体目标和验收以 [任务书](../README.md) 为主。

## 项目结构与材料定位

- [../attention.py](../attention.py)：单头注意力基础演示，可复核矩阵形状、因果掩码及位置顺序。
- [../requirements.txt](../requirements.txt)：演示所需 NumPy。
- [../README.md](../README.md)：Basic/Advance 任务书（项目主说明）。

## 建议阅读与使用顺序

1. 先完成 Basic 单头数值实验，再读 README.md 的 Advance 目标。
2. 以 attention.py 为最小基线；按任务书扩展多头、位置表示与模块组合。
3. 对同一输入比较掩码、头数与参数变化，保存张量形状、权重图和因果性测试。
4. 根目录现有脚本只覆盖单头示例，完整 Transformer 结构由学生继续实现。

## 本地起步

从项目根目录运行：

    python -m pip install -r requirements.txt
    python attention.py
