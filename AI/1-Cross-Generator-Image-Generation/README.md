# AI1：跨生成器图像检测

## A 问题是什么

AI 生成图检测要做的是：把扩散模型 / GAN 合成的图像，和真实照片分开。只在某一个生成器上训练时，小分类器往往就能分开；但换一个生成器后，分数可能掉到接近随机。本项目分两段：Basic 先在**一个生成器**上训练最简二分类器，把流程跑通；Advance 再按论文思路做跨生成器评测，并尝试让模型在未见生成器上也能区分，提高泛化。

| 阶段 | 工作量安排 | 难度 | 完成后的能力 |
| --- | --- | --- | --- |
| Basic | 一周内约 10–20 小时 | easy | 知道检测器是怎样打分的，在一个生成器的小数据上训练最简二分类器 |
| Advance | 完成 Basic 后再用六周 | medium | 复现冻结 CLIP-ViT-B/32，比较它和 Basic 在未见生成器上的泛化 |

两个阶段都不需要从零训练 GAN 或扩散模型来“造图”。Basic 的“简易”指**简易检测器**，数据量不必大，效果不必好。不能把课程结果说成能识别所有 AI 图像。

### Basic：在一个生成器上训练最简检测器

#### 1 学习目标

先搞清检测、标签、同分布测试，以及“一个神经元如何把图变成真/假”。
Basic 不要求另外提交书面问答。

#### 2 本周用到的神经网络（先读这段）

没学过神经网络也可以做 Basic。**先读完这一小节，再按需点开博客。** 不必手推反向传播，也不必先学微积分。

**图像就是一堆数字。** 一张灰度 32×32 的图 = 1024 个 0–1 的数。彩色图则是红、绿、蓝三张这样的表。程序看不到“猫”或“AI 图”这几个字，只看到这些数。`basic/student/train_binary.py` 就是把图变成灰度 32×32，再拉成一列数字。

**一个神经元 = 加权求和再 squish。** 每个输入乘一个权重，全部加起来，再加一个偏置，得到 `score`：

```text
score = w1*x1 + w2*x2 + ... + b
```

若再把 score 塞进 Sigmoid（S 形曲线），输出会挤到 0 和 1 之间，可以当成
`P(synthetic)`；这叫逻辑回归，也是仓库脚本实际用的东西。

**训练就是改权重。** 假图希望 score 变大（或概率靠近 1），真图希望 score 变小（或概率靠近 0）。看错了就按误差把权重微调一点点。衡量“错得多离谱”的常用函数叫交叉熵，知道它在惩罚“很自信但判错”即可。

**小神经网络只是把神经元叠起来。**

| 名字 | 人话 | Basic 要不要 |
| --- | --- | --- |
| 逻辑回归 / 单层线性 | 一个神经元看全部像素 | **默认就用这个** |
| 多层感知机 MLP | 先把像素压成若干中间数，再分类 | 可选 |
| CNN | 用 3×3 小窗口在图上滑，先找边缘/纹理，再分类 | 可选；图像任务里更常见 |
| CLIP-ViT-B/32 | 把图压成 512 维向量的预训练图像编码器 | Basic 不用；Advance **必须用** |

训练循环可以记四步：读一批图 → 算出预测 → 算损失 → 更新权重。测试时不再更新权重，只报没见过的图上对了多少。

**不要求全部阅读或分别交笔记。** 零基础：先读上面这段，再 B1 或 B2，然后对照 B6 跑脚本。已经会训练循环：直接 B5 → B7。知乎/博客可能改版，能对照概念即可。

| 编号 | 材料 | 建议用法 |
| --- | --- | --- |
| B1 | [知乎：神经网络 15 分钟入门](https://zhuanlan.zhihu.com/p/65472471) | 最浅的一篇：加权求和、激活、输出当概率 |
| B2 | [B 站：3Blue1Brown《神经网络的结构》官方双语](https://www.bilibili.com/video/BV1bx411M7Zx/) | 约 20 分钟；用手写数字的像素当神经元，和本项目把 32×32 拉平是同一思路。只看第 1 集 |
| B3 | [知乎：0 基础神经网络原理（一个神经元算什么）](https://zhuanlan.zhihu.com/p/377513272) | 只读“一个神经元”和 Sigmoid 两节；后面手写训练可跳过 |
| B4 | [知乎：Logistic 回归 = 最基础的神经网络](https://zhuanlan.zhihu.com/p/38850641) | 用“像素排成一列 → 是不是猫”讲二分类，和本项目几乎同一件事 |
| B5 | [知乎：PyTorch 图像分类入门](https://zhuanlan.zhihu.com/p/39667289) | 对照读数据、训练循环、测试准确率；不必复现文中全部 epoch |
| B6 | [sklearn 逻辑回归文档](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html) | 不想写 PyTorch 时用；`train_binary.py` 走这条路 |
| B7 | [CIFAKE 数据集页](https://www.kaggle.com/datasets/birdy654/cifake-real-and-ai-generated-synthetic-images) | 32×32 小图；真图 CIFAR-10，假图主要来自 SD v1.4。Basic 只用这一个生成器 |
| B8 | [Pillow 读图教程](https://pillow.readthedocs.io/en/stable/handbook/tutorial.html) | 打开图片、转灰度、resize |
| B9 | [知乎：CNN 30 分钟入门](https://zhuanlan.zhihu.com/p/635438713) | **仅在你决定写小卷积网时再读**；卷积=滑窗、池化=缩小 |
| B10 | [《动手学深度学习》多层感知机（选读）](https://zh.d2l.ai/chapter_multilayer-perceptrons/mlp.html) | 想看教材版的隐藏层和 ReLU 时再读；跳过推导 |

Basic 不要求 ResNet、GPU、跨生成器。B9、B10 可以等真正写更深的网络再看。交叉熵、反向传播的公式都不要求会默写。

#### 3 代码任务：最简二分类检测器

在**同一个生成器**的小数据上区分真/假。每类 100–500 张即可；CIFAKE 子集或 GenImage 里某一个生成器的小子集都可以。

```text
data/raw/
  real/<source_name>/*.jpg
  synthetic/<generator_name>/*.png
```

标签由上一级 `real/` / `synthetic/` 决定。最低要求：

1. 读图并统一尺寸（32×32 或 224×224 均可）。
2. 按文件划分训练/测试（例如 8:2）。测试图不得出现在训练中。Basic **不必**引入第二个生成器。
3. 训练最简检测器，任选其一：
   - 像素拉平 + 逻辑回归 / 一层线性模型（对应上一节的“一个神经元”）；
   - 极小 CNN 或一两层全连接；
   - 若已有 GPU，也可用 ResNet-18 微调，但不是 Basic 必需。
4. 打印训练准确率、测试准确率、测试样本数、所用生成器名称。不设分数线。
5. 对几张没见过的测试图打印预测。

```bash
cd basic
python -m pip install -r requirements.txt
python student/train_binary.py --input data/raw
```

`basic/student/train_binary.py` 是教学入口（灰度 32×32 + 逻辑回归）。可换成小网络，但不要为刷分换大模型。

**Basic 只要求：在你选的那一个生成器上，检测器能工作，数字来自真实运行。**

#### 4 Basic 提交与验收

提交源码、一次真实运行日志（训练/测试准确率、生成器名）。不要求跨生成器或论文复现。

验收：分类器能在单一生成器的小数据上训练，并在同分布测试集上给出准确率。

### Advance：跨生成器泛化（论文方法）

#### 1 学习目标与难度

Advance 的目标不再是把同一生成器上的准确率再刷高，而是：**换一个训练时没见过的生成器，仍然尽量能区分。** 常见现象是：端到端微调在训练用的生成器上接近满分，换到更不像的生成器后掉到接近随机；冻结预训练特征再做线性探针或 KNN，同分布未必最高，但跨生成器往往更稳。

| Goal | 学习目标与完成要求 | 难度 |
| --- | --- | --- |
| G1 | **理解失败模式：** 说明为何单生成器微调会学到指纹；同分布高分不等于跨生成器有效 | easy |
| G2 | **搭起来源隔离评测：** 训练只用生成器 A，最终测试至少包含未见生成器 B；真实图来源也要隔离 | easy |
| G3 | **复现 Ojha 方法（CLIP-ViT-B/32）：** 冻结官方 `ViT-B/32` 图像编码器提 512 维特征，再做线性探针或 KNN；不得换成 ResNet / 其他 ViT 交差 | medium |
| G4 | **输出切分与指标：** 每张图标明 source / split；分别输出同分布与跨生成器的 accuracy，以及 AUROC 或 F1 | easy |
| G5 | **比较并解释：** Basic 微调 vs 冻结特征方法；指出谁在未见生成器上更好，以及可能原因 | medium |

G1–G5 均需完成。不必下载全量基准，但**至少两个生成器**：一个训练、一个完全未见。有余力可再加第三个。

**六周要复现的是方法，不是论文全量实验。** 必须冻结官方 CLIP `ViT-B/32`（图像特征 512 维）。Ojha 原文常用更大的 `ViT-L/14`；本课用 B/32 是为了 CPU/小 GPU 也能抽特征。不要求训练 CLIP 本身，也不要求复现论文里全部生成器和全部消融。

#### 2 会用到的网络（同样先读这段）

Advance 只比 Basic 多三个词：**骨干、冻结、探针**。先用这段建立直觉，再读博客或论文。

可以把大网络想成两截：

```text
图像 → [骨干 / 特征提取器] → 一串数字（特征） → [小头 / 分类器] → real / synthetic
```

- **CLIP-ViT-B/32** 是 OpenAI 用大量「图 + 说明文字」训好的模型。本项目**只用图像编码器**：把 224×224 的图变成 **512 维**向量。`ViT-B/32` 表示视觉 Transformer、Base 规格、每块 32×32 像素。权重必须是官方 CLIP；不要换成 ResNet-18、自己训的 ViT，或未冻结的骨干来交差。
- **端到端微调**：骨干和小头一起改。同分布往往很高，但容易把“生成器 A 的独特痕迹”记成答案，换生成器 B 就崩。
- **冻结 CLIP**：图像编码器权重锁死，不再更新。只在 512 维特征后面接一个线性层（线性探针），或对特征做 KNN。Ojha 的想法是：专门端到端训 real/fake，容易记住某一个生成器的指纹；冻住的 CLIP 特征有时更能跨生成器。

KNN 不训练新网络：测试图的特征找训练集里最像的几张，它们多数是真还是假，就跟着投。这里的“像”是 CLIP 特征空间里的距离，不是文件名或像素逐点相等。

六周足够把冻结 CLIP-ViT-B/32 跑通。零基础先 A1、A2、A5，再对照 A6 和仓库脚本实现。

| 编号 | 材料 | 建议用法 |
| --- | --- | --- |
| A1 | [知乎：预训练和微调是什么](https://zhuanlan.zhihu.com/p/389842883) | 用图像分类分清 pre-train / fine-tune；对应“冻结骨干” |
| A2 | [知乎：PyTorch 迁移学习（冻骨干、只训最后一层）](https://zhuanlan.zhihu.com/p/27443713) | 看 `requires_grad = False` 再换最后一层；不必跑完 CIFAR-10 |
| A3 | [知乎：KNN 分类在干什么](https://zhuanlan.zhihu.com/p/76423064) | 近的邻居投票；Advance 是对**图像特征**做 KNN，不是对原始像素 |
| A4 | [CSDN：冻结特征 + 线性探针在干什么](https://blog.csdn.net/ZHY0091/article/details/148906251) | 冻住骨干、只训一层线性分类器；和 G3 同构，少样本部分可跳过 |
| A5 | [知乎：CLIP 原理极简版](https://zhuanlan.zhihu.com/p/646790176) | 图和文字都变成向量；本项目只用 `encode_image`，不必做图文检索 |
| A6 | [Ojha et al., Universal Fake Image Detectors（CVPR 2023）](https://arxiv.org/abs/2302.10174) | 主文献。读 Introduction + Method；课上用 `ViT-B/32` 复现其冻结特征 + 探针/KNN，不必上 `ViT-L/14` |
| A7 | [知乎：GenImage 跨生成器基准](https://zhuanlan.zhihu.com/p/683942893) | 中文看“训练生成器接近满分、未见生成器接近随机” |
| A8 | [知乎：AIGC 图像检测的现状与困境](https://zhuanlan.zhihu.com/p/1915086201364415272) | 捷径、压缩、同分布不可靠 |
| A9 | [博客园：CNNDetection](https://www.cnblogs.com/wujianming-110117/p/12516144.html) | 早期“一个生成器训练、多个生成器测试” |
| A10 | [知乎：Grad-CAM 看模型在看哪里](https://zhuanlan.zhihu.com/p/674661041) | 选 G6-B 时读；先有一个会分类的 CNN |

建议顺序：A1 → A5 → A4 或 A3 → 对照 A6 写代码。

#### 3 方法实现与过程展示（G2–G4）

| 方法 | 做什么 | 目的 |
| --- | --- | --- |
| Basic 检测器（复用） | 在生成器 A 上端到端训练像素/小网络分类器 | 同分布基线，通常很高 |
| 来源隔离测试 | 把 Basic 模型拿到未见生成器 B 上测 | 暴露指纹 |
| CLIP-ViT-B/32（必做） | 冻结官方 CLIP `ViT-B/32`，线性探针或 KNN | 提高跨生成器泛化 |
| 可选对照 | 频域统计 + 线性分类器 | 看深度模型是否只在吃频谱指纹 |

**G3 验收清单（缺一不可）：**

1. 加载官方 CLIP `ViT-B/32`，打印图像特征维度必须是 512。
2. `model.eval()`，全部 `requires_grad=False`；不得更新 CLIP 权重。
3. 用 CLIP 自带 preprocess（224×224）；不要自己随便 resize 后直接喂进去。
4. 只在生成器 A 的特征上拟合线性探针或 KNN（二选一即可）。
5. 在未见生成器 B 上输出 accuracy，并尽量加 AUROC 或 F1。

统一协议：

1. 训练只见生成器 A；最终跨生成器测试只用 B（可再加 C）。B 的任何图片都不得进入训练或选模型。
2. 同分布测试可以来自 A，但文件不与训练重叠；真实图也按文件划分，不要同一张真图既训练又测试。
3. 只在 A 的开发集上选超参数；B 只用一次。
4. 推理不用路径、文件名、EXIF；若 PNG/JPEG 与标签绑定，先统一转码再比。

建议规模：每个切分每类 200–1000 张即可，不必下载 GenImage 全量。记录生成器名称与版本。可先离线抽出 CLIP 特征再做探针/KNN；有 GPU 会快很多，CPU 也能抽，只是更慢。

```bash
cd advance
python -m pip install -r requirements.txt
python src/build_manifest.py --input data/raw --output data/manifest.csv \
  --train-gen <生成器A> --test-gen <生成器B> \
  --train-real-source <训练真图来源> --test-real-source <测试真图来源>
python src/train_pixel_baseline.py --manifest data/manifest.csv \
  --data-root data/raw --output outputs/pixel_metrics.json
python src/extract_clip_features.py --manifest data/manifest.csv \
  --data-root data/raw --output features/clip_vit_b32.npz
python src/train_probe.py --features features/clip_vit_b32.npz \
  --data-root data/raw --output-dir outputs/clip_probe
```

完整参数和输出说明见 `advance/README.md`。学生需要补全骨架中的 9 个 TODO，不能把
CLIP 骨干换成其他模型交差。

#### 4 比较方法并解释结果（G5 · medium）

主结果表至少包含下面三列（数字自己填）。同分布单独一列，每个未见生成器单独一列，不要揉成一个平均分。

| 方法 | 生成器 A（同分布） | 生成器 B（未见） |
| --- | ---: | ---: |
| Basic 检测器（像素/小网络，端到端） |  |  |
| 冻结 CLIP-ViT-B/32 + 线性探针或 KNN |  |  |

不要只输出平均分。若微调在 A 上 95%+、在 B 上接近 50%，通常说明它学到了 A 的指纹。
若冻结特征在 B 上高于微调，即使 A 上略低，也说明泛化更好。

程序应分别保存 Test-A 和 Test-B 的指标、逐样本预测，以及最多 10 张最自信的
Test-B 错误图。

#### 5 可选探索（不作提交要求）

有余力的学生可以自行选择一个方向继续尝试，不作必交要求。

| 方向 | 难度 | 重点理解的问题 | 对应资料 |
| --- | --- | --- | --- |
| 更多生成器 | medium | 再加一个与 A 更不像的生成器（如扩散 vs GAN），表会如何变？ | A7、A9 |
| 看模型在看哪里 | medium | 热力图若只亮边角或背景，高分还算证据吗？可用现成 Grad-CAM；不必自己实现 ViT 的完整 CAM | A10、A6 |
| JPEG / 缩放压力测试 | easy | 同分布模型在压缩后是否还在？ | A6、A8 |

## B 工作量安排与 Checkpoint

### Basic：一周，约 10–20 小时

按已接触 Python 文件读写、但**不一定学过神经网络**的学生估算。有深度学习经验的同学可能更快，不必为凑时长换大模型。

| 内容 | 预计用时 |
| --- | --- |
| 读神经网络最小说明书，理解分类流程 | 3–5 小时 |
| 准备单一生成器的小数据，读图 | 2–4 小时 |
| 训练最简检测器，看同分布准确率 | 3–6 小时 |
| 整理运行结果 | 1–2 小时 |
| 合计 | 约 10–16 小时 |

Checkpoint：源码、真实运行的同分布准确率、所用生成器。

### Advance：在 Basic 基础上追加六周

| 时间 | 对应 Goal 与难度 | 主要任务 | Checkpoint |
| --- | --- | --- | --- |
| 第 1–2 周 | G1、G2、G4：easy | 加入第二个生成器，先把 Basic 模型在 B 上测一遍 | 能展示 A 高、B 低或 A/B 都高，并说明切分 |
| 第 3–4 周 | G3、G5：medium | 按清单复现冻结 CLIP-ViT-B/32，做线性探针或 KNN，填主结果表 | 能证明骨干是 `ViT-B/32`、权重冻结，并给出 A/B 对比数字 |
| 第 5-6 周 | G4、G5：easy–medium | 完善指标、逐样本预测和错误样本输出 | 所有结果来自真实运行，Test-A/Test-B 分开保存 |

## C 问题的来龙去脉与发展过程

**从能把图做得更像，到需要检测器。** GAN 与扩散模型让合成图接近日常摄影。检测首先是一个二分类：在某一批真图和某一个生成器上，小模型往往就能分开。[CIFAKE](https://www.kaggle.com/datasets/birdy654/cifake-real-and-ai-generated-synthetic-images) · [神经网络 15 分钟入门](https://zhuanlan.zhihu.com/p/65472471)

**从“这一批上能分开”，到必须按生成器评测。** CNNDetection 展示过单生成器训练后向其他 CNN 生成器迁移；GenImage 则表明许多检测器在训练生成器上接近满分，在未见生成器上接近随机。[博客园 CNNDetection](https://www.cnblogs.com/wujianming-110117/p/12516144.html) · [知乎 GenImage](https://zhuanlan.zhihu.com/p/683942893)

**从专门学习 fake 痕迹，到借用更通用的视觉特征。** Ojha 等人指出，端到端 real/fake 网络容易把“不像训练时那些假图”的东西统统判成 real。冻结 CLIP 等特征再做 KNN 或线性探针，同分布未必最高，但跨生成器往往更稳。这就是 Advance 要亲自比较的事情。[Ojha et al.](https://arxiv.org/abs/2302.10174)
