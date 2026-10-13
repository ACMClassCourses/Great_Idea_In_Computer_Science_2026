# Mini Git Advance：学生版

本目录是 Advance 阶段下发给学生的项目起点。项目只提供最基本的对象概念、构建配置和全部本地测试，不限定 Object Store、Repository 或辅助函数的具体设计。

## 已提供内容

- `GitObject` 抽象基类；
- `Blob`、`Tree` 和 `Commit` 派生类的空声明；
- 一个最小的 `main.cpp`；
- CMake 构建配置；
- 全部本地输入输出测试。

## 需要完成的内容

需要自行设计并实现：

- Blob、Tree 和 Commit 保存的数据；
- 对象序列化、ID 分配和内容去重；
- Index；
- 多级路径和递归 Tree；
- Commit 及父提交关系；
- Branch 和 HEAD；
- checkout、完整版本恢复和未提交修改保护；
- 命令读取、输出和错误处理；
- 所需的类、源文件与辅助函数。

可以自由增加、删除或调整学生自己编写的类和私有接口，但必须保留 Blob、Tree、Commit 的对象关系，并保证程序行为符合总题面。

## 构建与测试

```bash
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

CMake 会自动编译 `src/` 下新增的 `.cpp` 文件。项目初始状态可以编译，但核心功能尚未实现，因此测试不会通过。
