"""bm25.py — 从零实现的 BM25 稀疏检索（TODO 2，学生版占位）。

不依赖任何检索库。对应 README Basic 代码任务 TODO 2（必做）。
`tokenize` 已给出（ASCII/数字按词、CJK 按单字，零依赖）；学生需实现
`fit` / `scores` / `search` 三个方法。如需对照，可参考 rank_bm25，但本项目要求自己写一遍。
"""

from __future__ import annotations

import math
import re
from collections import Counter

# CJK 统一表意文字区段（覆盖常用汉字）
_CJK = re.compile(r"[一-鿿]")


def tokenize(text):
    """分词：ASCII/数字按词，CJK 按单字（无分词依赖，可直接复用）。

    英文语料走空格分词；中文语料按字切分，使 BM25 在零依赖下也能工作。
    """
    if isinstance(text, (list, tuple)):
        return [str(t).lower() for t in text]
    text = str(text).lower()
    tokens = re.findall(r"[a-z0-9]+", text)
    for ch in text:
        if _CJK.match(ch):
            tokens.append(ch)
    return tokens


class BM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.chunks = []
        self._docs = []
        self._df = Counter()
        self._idf = {}
        self._avgdl = 0.0
        self._dl = []

    def fit(self, chunks):
        """TODO 2：统计词频、文档频率、平均长度与 idf。返回 self 以便链式调用。"""
        raise NotImplementedError(
            "TODO 2：实现 fit —— 用 tokenize 对每个 chunk 分词，统计文档频率 df、"
            "平均文档长度 avgdl，并计算 idf = log(1 + (N - f + 0.5) / (f + 0.5))。"
        )

    def scores(self, query):
        """TODO 2：对单个 query 返回每个文档的 BM25 得分列表（长度 = 文档数）。"""
        raise NotImplementedError(
            "TODO 2：实现 scores —— 对 query 的每个词，用 idf 与 (f, k1, b, dl, avgdl) "
            "计算 BM25 得分并累加。"
        )

    def search(self, query, k: int = 5):
        """TODO 2：返回得分最高的 k 个 (chunk, score)。"""
        raise NotImplementedError(
            "TODO 2：实现 search —— 调用 scores 后按得分降序取前 k 个，"
            "返回 [(chunk, score), ...]。"
        )
