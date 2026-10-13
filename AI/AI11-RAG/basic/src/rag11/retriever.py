"""retriever.py — top-k 统一检索接口（TODO 5，sparse 已给出，hybrid 待补）。

对应 README Basic 代码任务 TODO 5。Hard 两条流程都复用本接口，确保比较时
检索结果一致。
"""

from __future__ import annotations

import numpy as np

from .bm25 import BM25
from .embed import Encoder
from .index import FaissIndex, rrf_fuse
from .ingest import Chunk, load_corpus


class Retriever:
    def __init__(
        self,
        chunks: list[Chunk] | None = None,
        corpus_dir: str | None = None,
        mode: str = "sparse",
        top_k: int = 5,
        bm25_k1: float = 1.5,
        bm25_b: float = 0.75,
    ):
        if chunks is None:
            assert corpus_dir is not None, "需提供 chunks 或 corpus_dir"
            chunks = load_corpus(corpus_dir)
        self.chunks = chunks
        self.mode = mode
        self.top_k = top_k
        self.bm25 = BM25(k1=bm25_k1, b=bm25_b).fit(chunks)
        self.encoder = None      # TODO 3：稠密检索时填充 Encoder
        self.faiss = None        # TODO 4：稠密检索时填充 FaissIndex

    def retrieve(self, query: str, k: int | None = None) -> list[tuple[Chunk, float]]:
        """TODO 5：按 mode 返回 top-k 的 (chunk, score)。"""
        k = k or self.top_k
        if self.mode == "sparse":
            return self.bm25.search(query, k)
        if self.mode == "dense":
            # TODO 5：用 self.encoder + self.faiss 做近邻检索
            raise NotImplementedError("TODO 5: 实现 dense 检索（启用 embed + index 后）")
        if self.mode == "hybrid":
            # TODO 5：分别取 sparse/dense 的 top-k，再用 rrf_fuse 融合
            raise NotImplementedError("TODO 5: 实现 hybrid 检索（启用 embed + index 后）")
        raise ValueError(f"未知 mode: {self.mode}")
