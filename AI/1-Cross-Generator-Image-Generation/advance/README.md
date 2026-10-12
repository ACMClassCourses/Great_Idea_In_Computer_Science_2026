# Advance：跨生成器图像检测（学生版）

## 你要完成什么

Basic 只回答“模型能否区分同一个生成器中的真/假图”。Advance 要回答更难的问题：

> 只使用生成器 A 的假图训练，模型能否识别训练时从未见过的生成器 B？

你需要比较两种方法：

1. 已提供的 Basic 基线：32×32 灰度像素 + 逻辑回归。
2. 你需要补全的方法：冻结官方 CLIP `ViT-B/32`，提取 512 维图像特征，再训练一个
   逻辑回归线性探针。

本阶段不是训练 CLIP，也不是生成图片。Generator B 只能用于最终测试，不能参与训练、
选超参数或选择阈值。

## 数据要求

至少准备两个不同生成器和两个真实图来源，每组建议 200–1000 张：

```text
data/raw/
├── real/
│   ├── <train_real_source>/*
│   └── <test_real_source>/*
└── synthetic/
    ├── <generator_a>/*
    └── <generator_b>/*
```

- A 用于训练、开发和同生成器测试；B 只进入 `test_b`。
- 训练和测试真实图来源也要分开。
- `test_a` 与 `test_b` 使用同一批测试真实图，从而更公平地比较 A 与 B。
- 每个 split 内的 real 和 synthetic 数量应相同；多余图片可以暂不使用。
- 标签不能通过文件名、PNG/JPEG 格式、水印、尺寸或重复图片泄漏。
- 若真图全是 JPEG、假图全是 PNG，应先统一转码后再比较。

## 9 个必做 TODO

| TODO | 文件 | 要完成的内容 |
| --- | --- | --- |
| 1 | `build_manifest.py` | 扫描图片并登记 path、label、source |
| 2 | `build_manifest.py` | 建立 Train/Dev-A/Test-A/Test-B，检查来源隔离与泄漏 |
| 3 | `extract_clip_features.py` | 加载官方 CLIP `ViT-B/32` 和官方 preprocess |
| 4 | `extract_clip_features.py` | 设置推理模式并冻结全部 CLIP 参数 |
| 5 | `extract_clip_features.py` | 分批调用 `encode_image` 提取特征 |
| 6 | `extract_clip_features.py` | L2 归一化、验证 512 维并保存 `.npz` |
| 7 | `train_probe.py` | 只在 Train-A 上拟合线性探针 |
| 8 | `train_probe.py` | 分别计算 Dev-A、Test-A、Test-B 指标 |
| 9 | `train_probe.py` | 保存预测，并导出最自信的 Test-B 错误 |

`utils.py`、`train_pixel_baseline.py` 和命令行框架已经提供，不需要修改。TODO 应按提示自己
完成，不要更换 CLIP 型号，也不要对 CLIP 做微调来代替冻结特征实验。

## 安装与运行顺序

在 `advance` 目录执行：

```bash
python3 -m pip install -r requirements.txt
```

### 1. 建立数据清单

```bash
python3 src/build_manifest.py \
  --input data/raw --output data/manifest.csv \
  --train-gen generator_a --test-gen generator_b \
  --train-real-source train_photos --test-real-source test_photos
```

检查输出中的四个 split 都同时包含 real 和 synthetic。

### 2. 跑 Basic 基线

```bash
python3 src/train_pixel_baseline.py \
  --manifest data/manifest.csv --data-root data/raw \
  --output outputs/pixel_metrics.json
```

### 3. 提取一次 CLIP 特征

```bash
python3 src/extract_clip_features.py \
  --manifest data/manifest.csv --data-root data/raw \
  --output features/clip_vit_b32.npz
```

首次运行会下载官方权重。程序应打印或验证特征形状为 `(图片数, 512)`。有 GPU 时可加
`--device cuda`；CPU 也能运行，但会较慢。

### 4. 训练线性探针并评测

```bash
python3 src/train_probe.py \
  --features features/clip_vit_b32.npz --data-root data/raw \
  --output-dir outputs/clip_probe
```

`predictions.csv` 至少应包含：`path, source, split, label, prediction,
p_synthetic, correct`。`errors_test_b.csv` 至少应包含 Test-B 错误的路径、标签、预测和概率。

## 如何读结果

必须把 Test-A 和 Test-B 分开输出：

| 方法 | Test-A Accuracy | Test-A AUROC | Test-B Accuracy | Test-B AUROC |
| --- | ---: | ---: | ---: | ---: |
| 像素逻辑回归 | | | | |
| 冻结 CLIP + 线性探针 | | | | |

如果像素基线在 A 上很高、B 上接近随机，说明它可能学到了 A 的特定指纹。如果 CLIP 在
A 上略低但在 B 上更高，可以认为它在本实验设置下泛化更稳。不强制要求 CLIP 取得更高分数，
但程序必须完成正确的数据切分、冻结和评测。

## 需要完成的代码与输出

学生只需要补全代码并产生下列输出：

- 补全全部 9 个 TODO 的源码；
- 已正确填写 `source` 和 `split` 的 `manifest.csv`（不必把整个公开数据集交进仓库）；
- Basic 基线与 CLIP 探针的指标文件；
- 逐样本预测，以及最多 10 张最自信的 Test-B 错误图。

验收时会检查：Generator B 是否完全未参与训练；官方 CLIP 是否为 `ViT-B/32`；特征是否
为 512 维；骨干是否全部冻结；Test-A/Test-B 是否分开输出；结果是否来自真实运行。
