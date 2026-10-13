"""utils.py — Advance 已提供的辅助工具（不需要修改）。

提供 jsonl 读写、原子断言拆分的简单规则、以及标签合法性校验。
"""

from __future__ import annotations

import json
from pathlib import Path


def load_jsonl(path: str | Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def save_jsonl(path: str | Path, rows: list[dict]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_documents(path: str | Path) -> list:
    """读取 documents.jsonl 为 rag11 的 Chunk 列表（每篇文档一个块）。

    让 Advance 使用自己的语料而非根目录 data/demo；Retriever(chunks=...) 直接复用。
    """
    from rag11.ingest import Chunk

    docs = load_jsonl(path)
    return [
        Chunk(
            id=f'{d["id"]}#0',
            doc_id=d["id"],
            text=d["text"],
            source=d.get("source", ""),
        )
        for d in docs
    ]


# 合法标签集合（与根 README 定义一致）
VALID_LABELS = {"supported", "contradicted", "insufficient", "irrelevant"}


def validate_label(label: str) -> bool:
    return label in VALID_LABELS


def split_claims(answer: str) -> list[str]:
    """简单规则：按句号/分号/换行拆成候选原子断言。

    TODO 5 可自行替换为更强的拆分策略，但需保持 dev 上固定、可复现。
    """
    import re
    parts = re.split(r"[。；;\n]+", answer)
    return [p.strip() for p in parts if p.strip()]
