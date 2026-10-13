# 量子密码 · Basic

本目录是学生下发入口。完整课程要求以 [Basic 任务书](materials/任务书-Basic.md) 为准；[OJ 说明](materials/OJ-说明.md) 只解释自动检查部分。

## 目录结构

- [下发压缩包](04-量子密码-Basic.zip)：可直接下载、解压后独立使用。
- [materials/](materials/)：与压缩包相同的展开内容，便于在 GitHub 上阅读。
- [下发说明](materials/下发说明.md)：介绍包内文件与验收边界。
- [basic_circuits.py](materials/basic_circuits.py)：H/X/Z、电路演化与固定种子抽样的参考演示。
- [README-示例代码.md](materials/README-示例代码.md)：演示运行方法。
- 任务书 Basic 部分：Q1–Q3、四组电路与至少 1000 次模拟测量。

## 建议阅读与使用顺序

1. 先读 Basic 任务书，分清量子态、相位、测量、QKD 和后量子密码。
2. 手算 I、H、HH、HZH 的最终态及理论概率，再运行 basic_circuits.py 比较抽样频数。
3. 记录随机种子、shot 数、电路图、计数与解释，完成 Q1–Q3。
4. OJ 说明只检查单比特门序列的理论概率；参考演示不读取 OJ 标准输入。

从解压后的包顶层运行相应命令：

    python basic_circuits.py --shots 1000 --seed 20260929

经典模拟器的抽样是模拟结果，不是物理量子随机数。

完成 Basic 后，再读 [Advance 说明](../advance/README.md)。
