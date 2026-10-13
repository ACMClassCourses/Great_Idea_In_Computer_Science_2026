# 快照比较本地测试

本目录提供十三组输入输出测试，编号为 1-11、15、16。每组由 `<编号>.in` 和 `<编号>.out` 组成，输入是两份文本快照，输出是按文件名排序的变化日志。

在 `basic/` 目录完成 `src/monitor.cpp` 后，可以核对单组测试：

```bash
g++ -std=c++17 -O2 src/monitor.cpp -o monitor
./monitor < testcases/1.in
```

本地测试用于检查比较逻辑。Basic 还必须完成真实目录轮询和手工测试，具体要求见 [Basic 任务说明](../README.md)。
