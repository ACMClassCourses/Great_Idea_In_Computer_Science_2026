# Basic 线性版本快照

完整行为、例子与 Q1-Q5 见 [项目任务书](../README.md) 的 Basic 部分。本阶段从零编写 C++17 程序，按本地命令测试验收。

用 `map<string,string>` 保存暂存文件，用 `vector<Commit>` 保存提交。实现 `add`、`commit`、`log`、`show` 和 `exit`，检查旧快照独立、未修改文件保留和父提交关系。

自行创建 `src/main.cpp` 后，在本目录编译运行：

```bash
g++ -std=c++17 -O2 src/main.cpp -o minigit-basic
./minigit-basic < input.txt
```

至少保留六组命令及预期结果，覆盖两次提交、空文件、多行内容、修改后未提交、重复提交和错误编号。按本地测试验收，提交源码、运行说明、测试记录和 Q1-Q5。

完成后阅读 [Advance 说明](../advance/README.md)。
