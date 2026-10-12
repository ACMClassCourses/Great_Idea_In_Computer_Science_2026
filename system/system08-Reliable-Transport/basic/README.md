# 可靠传输 · Basic

本目录是学生下发入口。完整课程要求以 [Basic 任务书](materials/任务书-Basic.md) 为准；[OJ 说明](materials/OJ-说明.md) 只解释自动检查部分。

## 目录结构

- [下发压缩包](07-可靠传输-Basic.zip)：可直接下载、解压后独立使用。
- [materials/](materials/)：与压缩包相同的展开内容，便于在 GitHub 上阅读。
- [下发说明](materials/下发说明.md)：介绍包内文件与验收边界。
- [src/main.cpp](materials/src/main.cpp)：C++17 停止等待模拟器的 TODO。
- [CMakeLists.txt](materials/CMakeLists.txt)：构建入口；[README.md](materials/README.md) 是协议与运行说明。
- [public-tests/](materials/public-tests/)：公开输入输出样例。

## 建议阅读与使用顺序

1. 阅读 Basic 任务书和包内 README.md，先画 DATA/ACK 正常、丢数据、丢 ACK 时间线。
2. 在 src/main.cpp 完成事件顺序、累计 ACK、超时重传和重复包去重。
3. 编译并跑公开样例；保留六组以上场景的配置、日志和 RESULT 行。
4. OJ 说明只核对确定性模拟结果；Q1–Q5、两条时间线和完整测试记录需另交。

从解压后的包顶层运行相应命令：

    cmake -S . -B build
    cmake --build build
    ./build/reliable_transport_basic < public-tests/1.in

从解压包的顶层目录运行上述命令；Windows 可使用生成的可执行文件路径。

完成 Basic 后，再读 [Advance 说明](../advance/README.md)。
