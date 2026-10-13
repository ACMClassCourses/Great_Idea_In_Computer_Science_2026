# Advance 测试点

测试数据按 `example<n>.in` / `example<n>.out` 成对保存，编号 `1` 到 `8`，由 `CMakeLists.txt` 注册为 ctest 用例。除行尾换行差异外，程序的标准输出必须与 `.out` 完全一致（比对使用 `diff --strip-trailing-cr`，LF 与 CRLF 视为相同）。

| 编号       | 覆盖内容                                                                    |
| -------- | ----------------------------------------------------------------------- |
| example1 | README 的演示输入：`mkdir`/`cd`、`<` + 多级管道 + `tee` + `>`，并核对 `docs` 下三个文件内容一致 |
| example2 | 绝对/相对路径、`.`、`..`、根目录的 `..` 仍是根目录                                        |
| example3 | 文件与目录同名冲突、`mkdir` 重名、`cd`/`cat`/`ls` 的类型错误                              |
| example4 | 多级管道、`tee` 的副作用、`cat` 多文件连接、`>` 与 `<`                                   |
| example5 | 深层嵌套路径、绝对路径、相对路径与 `..` 的混用                                              |
| example6 | 组合语法错误：空管道段、缺少重定向目标、重定向位置不合法、`cd` 出现在管道中                                |
| example7 | 中途失败：错误不传给下游、已成功的 `tee` 不回滚                                             |
| example8 | `tee` 建新文件、父目录缺失、覆盖目录、`mkdir` 重名；无上游 `cat` 与 `echo` 的输出                 |

期望输出中的错误行格式见上一级 `README.md` 的「错误格式」一节：任何错误都只输出一行 `ERROR`。

运行全部测试：

```bash
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

> **换行符**：`.in` 文件使用 CRLF 换行，请在分词前去掉行尾的 `\r`；`.out` 同样是 CRLF，但比对时会忽略行尾换行差异。

