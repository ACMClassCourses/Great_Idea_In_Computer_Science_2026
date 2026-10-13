# OJ 题目材料：文件读写监控（Basic）—— 快照比较

本目录是项目「15-file_monitor」Basic 部分的 OnlineJudge 配套材料，供负责上传 OJ 的同事使用。**注意：OJ 题目只覆盖 Basic 中的"快照比较"纯函数（交付物②）；真实目录轮询监控器（交付物①）刻意不提供骨架、也不在 OJ 上评测，由学生从零编写并在本机演示验收**（见项目 README 的 Basic 第 2、4 节）。

- `src/monitor.cpp`：**下发给学生**的代码框架（含 `// TODO` 与英文引导注释），也可作为 OJ 附件发布；
- `testcases/`：全部评测数据，`N.in` / `N.out` 成对，共 16 个测试点，附 `config.json`（分组与时空限制）；
- 参考答案与数据生成器在 `ta/include/`（不下发）：`monitor_solution.cpp` 已对本目录全部测试点逐一验证通过（字节级一致）。

## 题面（可直接粘贴到 OJ 题目描述）

**题目描述**

一个文件监控器每隔一段时间对目录做一次快照，记录每个普通文件的名字、大小和最后修改时间。给定前后两次快照，请输出目录的变化日志。

**输入格式**

```text
N0
<name> <size> <mtime> <type>     （共 N0 行，旧快照）
N1
<name> <size> <mtime> <type>     （共 N1 行，新快照）
```

- `name`：文件名，不含空白字符，仅含字母、数字、`.`、`_`、`-`，长度不超过 64；
- `size`：文件大小，0 ≤ size ≤ 10⁹；
- `mtime`：最后修改时间的逻辑时钟读数，0 ≤ mtime ≤ 10¹⁸（需要 64 位整数）；
- `type`：`F` 为普通文件，`D` 为子目录；子目录条目不参与比较，应直接忽略；
- 0 ≤ N0, N1 ≤ 100000；同一快照中普通文件名不重复；条目按任意顺序给出。

**输出格式**

对每个发生变化的普通文件输出一行，所有行按文件名字典序（按字节比较）排列：

| 情况 | 输出 |
| --- | --- |
| 新快照有、旧快照没有 | `CREATE <name>` |
| 旧快照有、新快照没有 | `DELETE <name>` |
| 两边都有，但 size 或 mtime 不同 | `MODIFY <name>` |

两边都有且两项都相同的文件不输出；没有任何变化时输出为空。重命名按「DELETE 旧名 + CREATE 新名」处理，不输出任何重命名事件。

**样例输入**

```text
2
a 10 1 F
b 20 1 F
2
a 12 2 F
c 20 1 F
```

**样例输出**

```text
MODIFY a
DELETE b
CREATE c
```

**数据范围与提示**

- 0 ≤ N0, N1 ≤ 100000，大规模测试点要求近似 O(N log N) 的实现（两重循环的逐一查找会超时）；
- 建议 C++17。`mtime` 的最大值超过 32 位整数范围；
- 评测为全文精确比较，注意输出末尾换行、行内只有一个空格。

## 上传与打包说明

1. 在 OJ 后台新建题目（建议标题「文件监控：快照比较」），粘贴上方题面；
2. 测试数据用「数据 (zip)」上传，**格式要求严格**（见 OJ 官方帮助页「如何创建数据包？」/ `/OnlineJudge/help/admin/data-format`）：**压缩包文件名必须是 `题号.zip`**（题号是数据库主键 id），且**包内顶层是以题号命名的文件夹**，文件放在其中：`题号.zip/题号/1.in`、…、`题号.zip/题号/config.json`（结构与 A+B 数据包 `1000.zip/1000/…` 一致）。`config.json` 缺失或路径不对会报"需要 json 文件"之类的错误。在本目录执行（把 `<ID>` 换成实际题号，**两处都要换**）：

   ```bash
   cd testcases && mkdir -p <ID> && cp *.in *.out config.json <ID>/ && zip -r ../<ID>.zip <ID> && rm -rf <ID>
   ```

   若使用「数据（GUI）」上传，则逐点上传 `.in`/`.out` 并按 `config.json` 手工建组：simple（1–6）30 分、complex（7–11）30 分、large（12–14，时限 2000 ms）30 分、robust（15–16）10 分；其余测试点时限 1000 ms，内存均 256 MiB，无需 SPJ（`SPJ: 0`）；
3. 如需重新生成或调整测试点，运行 `python3 ta/include/gen_testcases.py include/testcases`（生成器与参考答案相互独立，可交叉验证）。

## 测试点一览

| 编号 | 分组 | 考查点 |
| --- | --- | --- |
| 1 | simple | README Q5 样例（MODIFY/DELETE/CREATE 各一，可手算） |
| 2 | simple | 旧快照为空，全部 CREATE |
| 3 | simple | 新快照为空，全部 DELETE |
| 4 | simple | 两快照相同，输出为空 |
| 5 | simple | 两快照均为空 |
| 6 | simple | 只有子目录条目，全部忽略 |
| 7 | complex | 乱序输入 + ASCII 字典序（大写、点号、下划线、数字开头文件名） |
| 8 | complex | 重命名 = DELETE + CREATE（元数据相同也不是同一文件） |
| 9 | complex | 仅 mtime 变化 / 仅 size 变化都算 MODIFY |
| 10 | complex | 文件变目录（DELETE）、目录变文件（CREATE） |
| 11 | complex | 200 条目混合操作，混入目录条目，乱序 |
| 12 | large | 10 万条目：10% 删除 + 45% 修改 + 10% 新增 |
| 13 | large | 10 万条目完全相同，输出为空 |
| 14 | large | 10 万全删 + 10 万全建，输出 20 万行 |
| 15 | robust | 极端值：size=0、mtime=0、mtime 接近 64 位上限 |
| 16 | robust | 大小写敏感与特殊字符文件名 |
