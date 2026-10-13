# AI-11 Basic：最简 RAG

## 目标

在自带的小型语料上完成“文档切分 → BM25 检索 → 生成带引用的回答”，并输出检索块及引用映射。Basic 重点是从零实现 BM25；稠密检索为可选增强。

## RAG 流程

文档会被切成带 ID 的文本块。程序根据问题检索 top-k 文本块，再将问题与文本块一起交给生成模型，并要求每个事实性陈述标出对应引用。引用编号应能映射回本次检索结果。

## 目录

```text
basic/
├── configs/default.yaml
├── data/demo/                 # 自带短文档语料
├── examples/                  # 自检、建索引、问答演示
├── src/rag11/
│   ├── ingest.py              # TODO 1：加载语料并切块
│   ├── bm25.py                # TODO 2：从零实现 BM25（必做）
│   ├── embed.py               # TODO 3：句向量编码（可选）
│   ├── index.py               # TODO 4：RRF / Faiss（可选增强）
│   ├── retriever.py           # TODO 5：统一检索接口
│   ├── prompts.py
│   └── generator.py           # TODO 6：模型调用与引用解析
└── outputs/
```

## 必做任务

| TODO | 文件 | 内容 |
|---|---|---|
| 1 | `ingest.py` | 实现 `chunk_text` 和 `load_corpus`，返回带 ID 与来源的文本块 |
| 2 | `bm25.py` | 从零实现词频、文档频率、IDF、BM25 得分与 top-k 搜索，不调用检索库 |
| 5 | `retriever.py` | 完成 sparse 检索统一接口 |
| 6 | `generator.py` | 拼接 prompt 并调用模型，返回回答与 `citation_ids` |
| 7 | `examples/02_query_demo.py` | 串联建索引、检索、生成，打印问题、命中块、回答及引用 |

TODO 3、4 的稠密向量检索为可选增强。默认配置使用 sparse 模式。`prompts.py` 和命令行框架已提供。

## 安装与运行

在 `basic/` 目录执行：

```bash
python -m pip install -r requirements.txt
python examples/00_self_check.py
python examples/02_query_demo.py --question "输入一个问题"
```

需要真实模型时，在 `configs/default.yaml` 配置兼容接口，并设置对应 API key；也可以先使用代码中的离线 stub 检查流程，但 stub 输出不能作为正式运行结果。

## 提交与验收

提交源码、一次真实运行记录（问题、检索块、回答、引用编号）及所用语料说明。检查引用编号能够对应检索块，并能在小语料上跑通检索到生成的完整流程。

## 建议阅读

- [RAG 原论文（Lewis et al.）](https://arxiv.org/abs/2005.11401)
- [ALCE：生成带引用的文本](https://arxiv.org/abs/2305.14627)
- [sentence-transformers 文档](https://www.sbert.net/)
- [BM25 参考实现 rank_bm25](https://github.com/dorianbrown/rank_bm25)
- [OpenAI API 文档](https://platform.openai.com/docs)

完成 Basic 后，可继续做同级目录中的 `../hard/`。
