"""embed.py — 文本向量化封装（TODO 3，可选增强；默认未启用）。

稠密检索是可选增强，不装 sentence-transformers 也能跑 Basic 的纯 BM25 路径。
"""

from __future__ import annotations

import numpy as np


class Encoder:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _lazy_load(self):
        if self._model is None:
            # TODO 3（可选）：启用稠密检索时取消下一行注释并 pip install sentence-transformers
            # from sentence_transformers import SentenceTransformer
            # self._model = SentenceTransformer(self.model_name)
            raise NotImplementedError("TODO 3: 启用 sentence-transformers 后删除此异常")
        return self._model

    def encode(self, texts: list[str]) -> np.ndarray:
        """TODO 3：批量编码，返回归一化向量 (n, dim)。"""
        model = self._lazy_load()
        return np.asarray(model.encode(texts, normalize_embeddings=True))
