"""ingest.py — 语料加载与切分（TODO 1，学生版占位）。

对应 README Basic 代码任务 TODO 1。学生需实现 `chunk_text`（切分策略）与
`load_corpus`（读目录、调用切分、返回带 id/source 的块列表）。`Chunk` 已给出，
可用作返回结构。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Chunk:
    id: str           # 形如 "<doc_id>#<idx>"
    doc_id: str
    text: str
    source: str = ""  # 来源文件名，用于引用与隔离评测
    title: str = ""


def chunk_text(text: str, doc_id: str, size: int = 400, overlap: int = 80,
               source: str = "") -> list[Chunk]:
    """TODO 1：把一段文本切成若干带 id 的块。

    实现提示：可先按空行分段，再把过长段落按定长滑动窗口切分；也可改成纯定长或按标题切分。
    返回 ``list[Chunk]``，其中 ``id`` 形如 ``f"{doc_id}#{idx}"``。
    """
    raise NotImplementedError(
        "TODO 1：实现 chunk_text —— 把 text 切成带 id 的 Chunk 列表"
        "（段落优先 + 定长兜底，或其它策略）。"
    )


def load_corpus(corpus_dir: str | Path) -> list[Chunk]:
    """TODO 1：读取目录下所有 .md/.txt，切分后返回带 id/source 的块列表。

    实现提示：递归遍历 ``corpus_dir``，对 .md/.txt 读文本并调用 ``chunk_text``；
    ``source`` 取文件名，便于后续隔离评测。
    """
    raise NotImplementedError(
        "TODO 1：实现 load_corpus —— 遍历目录、读取 .md/.txt、调用 chunk_text，"
        "返回 list[Chunk]。"
    )
