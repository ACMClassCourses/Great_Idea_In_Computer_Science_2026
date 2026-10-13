# 时间序列需求预测 · Basic

本目录是学生下发入口。完整课程要求以 [Basic 任务书](materials/任务书-Basic.md) 为准；[OJ 说明](materials/OJ-说明.md) 只解释自动检查部分。

## 目录结构

- [下发压缩包](03-时间序列需求预测-Basic.zip)：可直接下载、解压后独立使用。
- [materials/](materials/)：与压缩包相同的展开内容，便于在 GitHub 上阅读。
- [下发说明](materials/下发说明.md)：介绍包内文件与验收边界。
- [starter.py](materials/starter.py)：时间审计、时间戳查找与三基线的 TODO。
- [README.md](materials/README.md) 和 [requirements.txt](materials/requirements.txt)：本地运行与依赖。
- outputs/：保存数据卡、切分日期、指标及曲线。

## 建议阅读与使用顺序

1. 阅读 Basic 任务书，明确预测时刻和可见信息边界。
2. 完成时间戳排序、重复/缺失审计与按时间切分；上一天/周须按时间戳查找。
3. 在共同可评价时刻比较三条基线，报告 MAE、RMSE、WAPE 和样本数。
4. OJ 只检验整数小时输入上的数值；完整提交还要数据卡、真实日期、曲线与 Q1–Q5。

从解压后的包顶层运行相应命令：

    python starter.py < 自备测试.in

不要将时间戳缺失时的上一周同小时简单写成向上移动 168 行。

完成 Basic 后，再读 [Advance 说明](../advance/README.md)。
