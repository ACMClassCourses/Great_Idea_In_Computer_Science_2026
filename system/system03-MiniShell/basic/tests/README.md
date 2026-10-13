# Basic 测试点

测试数据按 `example<n>.in` / `example<n>.out` 成对保存，编号 `1` 到 `8`，由 `CMakeLists.txt` 注册为 ctest 用例。除行尾换行差异外，程序的标准输出必须与 `.out` 完全一致（比对使用 `diff --strip-trailing-cr`，LF 与 CRLF 视为相同）。

| 编号 | 覆盖内容 |
| --- | --- |
| example1 | README 的演示输入：重复 `touch` 不清空文件、重定向写入、`ls`、`pwd` |
| example2 | 空目录 `ls` 不输出、`pwd`、文件名字典序、空文件 `cat`、`echo` 的三种形式 |
| example3 | `echo one > a.txt` → `touch` → `echo two > a.txt` 的覆盖与保持（对应 Q5） |
| example4 | 五类错误（缺少参数、多余参数、未知命令、非法文件名、文件不存在）＋ 缺少重定向目标，且错误后继续执行 |
| example5 | 多词内容写入与覆盖、重复 `touch` |
| example6 | 文件名 ASCII 字典序（含 `-`、`.`、数字、`_`） |
| example7 | 无参数 `echo` 与空行输出；输入没有 `exit`，靠 EOF 结束 |
| example8 | 重复创建、覆盖写入、`ls`/`pwd` 与多余参数错误后的继续执行 |

期望输出中的错误行格式见上一级 `README.md` 的「错误格式」一节：任何错误都只输出一行 `ERROR`。

运行全部测试：

```bash
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

> **换行符**：`.in` 文件使用 CRLF 换行，请在分词前去掉行尾的 `\r`；`.out` 同样是 CRLF，但比对时会忽略行尾换行差异。
