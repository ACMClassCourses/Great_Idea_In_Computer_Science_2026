# 神经网络 · Advance

先完成 [Basic](../basic/README.md)。本阶段的具体目标和验收以 [任务书](../README.md) 为主。

## 项目结构与材料定位

- [../train.py](../train.py)：Basic MLP 训练与评测基线。
- [../requirements.txt](../requirements.txt)：PyTorch、torchvision 依赖。
- [../README.md](../README.md)：Basic/Advance 任务书（项目主说明）。

## 建议阅读与使用顺序

1. 先复现 train.py 的 MLP 损失、测试准确率和错误样本，固定数据与随机种子。
2. 阅读 README.md 的 Advance G1–G7；在独立文件中加入小型 CNN。
3. 用同一划分和预算比较 MLP/CNN，记录参数量、训练时间、指标和过拟合情况。
4. 分析具体错误图像与模型局限，不把 OJ 前向预检当成完整训练验收。

## 本地起步

从项目根目录运行：

    python -m pip install -r requirements.txt
    python train.py
