"""index.py — 稠密向量索引与融合（TODO 4；RRF 融合已给出，faiss 可选）。

- rrf_fuse：从零实现的 Reciprocal Rank Fusion（已给出可运行实现）。
- FaissIndex：稠密近邻索引（可选增强，默认未启用）。
"""

from __future__ import annotations

import numpy as np


def rrf_fuse(rankings: list[list[int]], k: int = 60) -> list[int]:
    """TODO 4（从零）：Reciprocal Rank Fusion。

    rankings 是多个检索器各自返回的 doc 下标排序（越靠前越相关）。
    对每个 doc 累加 score = sum_s 1/(k + rank_in_s)，按分数降序返回融合排序。
    """
    raise NotImplementedError(
        "TODO 4：实现 rrf_fuse —— 对每个 ranking 中的 doc 累加 1/(k + rank + 1)，"
        "返回按融合分数降序排列的 doc 下标列表。"
    )


class FaissIndex:
    def __init__(self):
        self._index = None
        self._vectors = None

    def build(self, vectors: np.ndarray) -> "FaissIndex":
        """TODO 4（可选）：启用稠密检索时取消注释并 pip install faiss-cpu。"""
        # import faiss
        # self._vectors = np.asarray(vectors, dtype="float32")
        # self._index = faiss.IndexFlatIP(self._vectors.shape[1])
        # self._index.add(self._vectors)
        raise NotImplementedError("TODO 4: 启用 faiss 后删除此异常")

    def search(self, q: np.ndarray, k: int = 5):
        """TODO 4（可选）：返回 (distances, indices)。"""
        raise NotImplementedError("TODO 4: 启用 faiss 后删除此异常")
