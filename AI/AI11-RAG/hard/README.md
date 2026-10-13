# AI-11 Hard：证据绑定与忠实度评测

## 目标

完成 Basic 后，复用 `../basic/src/rag11` 的检索与生成，比较普通 RAG 和断言—证据绑定流程。研究答案正确性、检索命中、证据支持、覆盖率、拒答与成本之间的关系。此阶段不要求训练模型。

## 文件

```text
hard/
├── configs/default.yaml
├── data/
│   ├── documents.jsonl       # 小型检索语料
│   └── questions.jsonl       # 仅含题目，不含参考答案或 gold evidence
├── src/
│   ├── utils.py              # JSONL、断言拆分与标签校验辅助函数
│   ├── baseline_rag.py       # TODO 1–2：普通 RAG
│   ├── evidence_bound.py     # TODO 3–5：断言—证据绑定
│   └── evaluate.py           # TODO 6–7：指标与失败案例
└── outputs/
```

Hard 通过相邻的 `basic/` 目录导入 `rag11`。请保留两个文件夹的相邻关系。

## 数据协议

提供的文档字段为 `id`、`text`、`source`；题目字段为 `id`、`question`。学生运行系统后生成响应，并自行设计测试集及人工标注。参考答案、gold evidence、响应和标注应由学生按研究设计另行准备；不得将测试标签放进提示词或用于开发集调参。

建议的产物字段：

- 响应：`question_id`、`system`、`answer`、`citation_ids`
- 断言标注：`question_id`、`claim_id`、`claim`、`evidence_ids`、`label`、`annotator`
- 标签：`supported`、`contradicted`、`insufficient`、`irrelevant`

至少 20% 的人工核验题由两人独立标注，再讨论分歧；至少覆盖 5 题。只有一人时可做隔期复标，并说明局限。

## 7 个必做 TODO

| TODO | 文件 | 内容 |
|---|---|---|
| 1–2 | `baseline_rag.py` | 使用与另一流程相同的语料、检索配置与模型，输出回答及引用编号 |
| 3 | `evidence_bound.py` | 按固定、可复现的规则把回答拆成原子断言 |
| 4 | `evidence_bound.py` | 为断言绑定当前检索结果中的证据，并判断四种支持标签 |
| 5 | `evidence_bound.py` | 对无依据断言执行保留、改写或拒答；不得把人工 gold evidence 传给系统 |
| 6 | `evaluate.py` | 计算准确率、引用支持率、无支持断言率、coverage、拒答率和成本，显式写出分母 |
| 7 | `evaluate.py` | 导出逐题结果、失败案例与 accuracy–support 对照图 |

两种流程必须使用相同的文档库、问题集、检索器、top-k、模型和解码设置；测试标签不得进入 prompt 或阈值选择。至少报告五个失败案例，并解释支持率、coverage 与拒答率的折中。分母为零时应标为 `N/A`。

## 安装与运行

在保留 `basic/` 与 `hard/` 相邻关系的前提下，在 `hard/` 目录执行：

```bash
python -m pip install -r requirements.txt
python src/baseline_rag.py --data data --output outputs/baseline.jsonl
python src/evidence_bound.py --data data --baseline outputs/baseline.jsonl --output outputs/evidence_bound.jsonl
python src/evaluate.py --baseline outputs/baseline.jsonl --evidence-bound outputs/evidence_bound.jsonl --annotations data/annotations.jsonl --output outputs/report.md
```

运行评测前，请依照你的数据划分和标注规范创建 `data/annotations.jsonl`，并按需调整模型与检索配置。没有 API 或生成条件时，可在研究方案中使用受限离线路线，但需清楚说明结论范围；本学生包不提供冻结回答样例。

## 提交

提交语料/问题数据卡、两条流程代码或离线协议、模型与检索配置、断言和证据日志、标注规范、一致性结果、指标分母、主结果及失败案例。展示中说明准确性、证据支持和遗漏之间的关系。
