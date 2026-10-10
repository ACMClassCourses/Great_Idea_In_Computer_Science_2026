# 支持向量机与群智能算法优化 · Basic

本目录是学生下发入口。完整课程要求以 [Basic 任务书](materials/任务书-Basic.md) 为准；[OJ 说明](materials/OJ-说明.md) 只解释自动检查部分。

## 目录结构

- [下发压缩包](02-SVM-Basic.zip)：可直接下载、解压后独立使用。
- [materials/](materials/)：与压缩包相同的展开内容，便于在 GitHub 上阅读。
- [下发说明](materials/下发说明.md)：介绍包内文件与验收边界。
- [starter.py](materials/starter.py)：训练/开发/测试协议的学生 TODO。
- [requirements.txt](materials/requirements.txt)：NumPy、scikit-learn 等本地依赖。
- [README.md](materials/README.md)：输出格式与实验提交说明；outputs/ 保存图和指标。

## 建议阅读与使用顺序

1. 阅读 Basic 任务书中最大间隔、C、gamma 与数据隔离的要求。
2. 在本机安装依赖后完成 starter.py；StandardScaler 与 SVC 必须在同一 Pipeline。
3. 仅用开发集选参数，冻结后在测试集评价一次，保存混淆矩阵、边界图或预测表。
4. OJ 说明只核对预测格式和准确率，不能代替数据泄漏审计与 Q1–Q5。

从解压后的包顶层运行相应命令：

    python -m pip install -r requirements.txt
    python starter.py < 自备测试.in

OJ 的 Python 运行环境不提供 scikit-learn；这个框架用于本地完整课程实验，不能把依赖它的脚本直接粘贴到 OJ。

完成 Basic 后，再读 [Advance 说明](../advance/README.md)。
