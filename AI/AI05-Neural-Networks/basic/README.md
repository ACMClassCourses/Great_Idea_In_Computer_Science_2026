# 神经网络 · Basic

本目录是学生下发入口。完整课程要求以 [Basic 任务书](materials/任务书-Basic.md) 为准；[OJ 说明](materials/OJ-说明.md) 只解释自动检查部分。

## 目录结构

- [下发压缩包](06-神经网络-Basic.zip)：可直接下载、解压后独立使用。
- [materials/](materials/)：与压缩包相同的展开内容，便于在 GitHub 上阅读。
- [OJ 3279 题面](materials/OJ-说明.md)：两层 MLP 的反向传播与整批训练，使用适合 GitHub 阅读的公式写法。
- [ACMOJ 导入版](materials/OJ-题面-ACMOJ.md)：供助教下载原始文件后导入题面；保留 ACMOJ 所需的下标转义。
- [下发说明](materials/下发说明.md)：介绍包内文件与验收边界。
- [train.py](materials/train.py)：MNIST MLP 的参考训练演示。
- [requirements.txt](materials/requirements.txt)：PyTorch 与 torchvision；[README-示例代码.md](materials/README-示例代码.md) 说明运行方法。
- 任务书 Basic 部分：Q1–Q5、训练日志、测试准确率与错误样本分析。

## 建议阅读与使用顺序

1. 阅读 Basic 任务书，先手算 AND 前向例子，再理解 784→64→ReLU→10。
2. 安装依赖并运行 train.py；首次运行会下载 MNIST，保存真实损失和测试日志。
3. 确认训练阶段与 eval()/no_grad() 测试阶段分离，整理预测或错误图像。
4. 按 OJ 3279 题面实现 softmax、交叉熵、反向传播和多步整批梯度下降，输出最终参数、预测类别与平均交叉熵；MNIST 训练日志、测试结果和错误分析仍需另外提交。

GitHub 阅读版和 ACMOJ 导入版的题目内容一致。ACMOJ 先解析 Markdown，再渲染公式，因此导入版对公式下标使用了反斜杠转义；上传题面时请使用导入版的原始文件。

从解压后的包顶层运行相应命令：

    python -m pip install -r requirements.txt
    python train.py

train.py 是课程训练演示，不读取 OJ 的标准输入，不能直接作为 OJ 提交。

完成 Basic 后，再读 [Advance 说明](../advance/README.md)。
