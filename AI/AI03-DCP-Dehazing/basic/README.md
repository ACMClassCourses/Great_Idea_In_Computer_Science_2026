# DCP 图像去雾 · Basic

本目录是学生下发入口。完整课程要求以 [Basic 任务书](materials/任务书-Basic.md) 为准；[OJ 说明](materials/OJ-说明.md) 只解释自动检查部分。

## 目录结构

- [下发压缩包](01-DCP去雾-Basic.zip)：可直接下载、解压后独立使用。
- [materials/](materials/)：与压缩包相同的展开内容，便于在 GitHub 上阅读。
- [下发说明](materials/下发说明.md)：介绍包内文件与验收边界。
- [starter.py](materials/starter.py)：学生完成 TODO 的最小数值框架。
- [requirements.txt](materials/requirements.txt)：本地依赖；[README.md](materials/README.md) 说明框架使用。
- [outputs/](materials/outputs/)：保存真实图像和中间结果的位置。

## 建议阅读与使用顺序

1. 阅读 Basic 任务书中的 Q1–Q5、四步 DCP 流程与提交要求。
2. 阅读 OJ 说明，区分小矩阵数值核对与真实图像实验。
3. 阅读框架 README，安装依赖，实现 starter.py 中的 TODO。
4. 自备有雾图像及来源记录，保存暗通道、透射率、恢复图和真实日志；再完成问答。

从解压后的包顶层运行相应命令：

    python -m pip install -r requirements.txt
    python starter.py < 自备测试.in

框架的标准输入格式只覆盖 OJ 数值核对。它依赖本地 NumPy，不能直接粘贴到 OJ 的 Python 运行环境；完整 Basic 还需真实图片、来源、过程图与 Q1–Q5。

完成 Basic 后，再读 [Advance 说明](../advance/README.md)。
