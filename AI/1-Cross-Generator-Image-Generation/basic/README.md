# Basic：在一个生成器上训练最简检测器

本目录对应根目录 `README.md` 里的 **Basic** 阶段（easy，约 10–16 小时）。
目标：在**同一个生成器**的小数据上，把真 / 假二分类的完整流程跑通，拿到一份
**真实运行**的同分布准确率。Basic 不要求跨生成器、不要求 ResNet、
不要求 GPU，效果不设分数线。

## 目录结构

```text
basic/
├── README.md                  # 本文件
├── requirements.txt           # Pillow / numpy / scikit-learn
├── make_demo_data.py          # 生成“冒烟测试”用小数据（非提交用）
├── data/raw/
│   ├── real/<source_name>/*.jpg
│   └── synthetic/<generator_name>/*.png
└── student/                   # 需要完成并提交的部分
    └── train_binary.py        # 带 TODO 的代码骨架
```

## 如何开始

1. 安装依赖：`python -m pip install -r requirements.txt`
2. 把真实小数据按上面的布局放进 `data/raw/`（**单一生成器**，每类 100–500 张即可，
   可用 CIFAKE 子集，或 GenImage 里某一个生成器的小子集）。
   - 没有真实数据时，可先 `python make_demo_data.py` 生成 demo 数据，仅用于确认
     代码能跑通，**不能作为提交结果**。
3. 打开 `student/train_binary.py`，按 `TODO 1`–`TODO 7` 补齐。
4. 运行并记录：
   ```bash
   python student/train_binary.py --input data/raw --seed 0
   ```

## 代码任务最低要求（对应文档第 3 节）

| 要求 | 实现位置 |
| --- | --- |
| 读图并统一尺寸（32×32 灰度） | `load_image` |
| 按文件划分 8:2 训练 / 测试 | `split_samples` |
| 训练最简检测器（像素拉平 + 逻辑回归） | `main` 中的 `LogisticRegression` |
| 打印训练 / 测试准确率、测试样本数、生成器名 | `main` 的结果输出段 |
| 对几张未见测试图打印预测 | `main` 的样例预测段 |

## 提交内容

- 补全全部 TODO 的 `student/train_binary.py`；
- 一次使用真实数据运行产生的日志，包含生成器名称、训练和测试准确率、
  测试样本数以及若干示例预测。
