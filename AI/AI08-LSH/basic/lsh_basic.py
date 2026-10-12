# -*- coding: utf-8 -*-
"""
LSH 近似最近邻检索 —— 基础版（学生版，E2LSH / 欧氏距离）

哈希族：E2LSH
    h(x) = floor( (a·x + b) / w )
    a：各维独立标准高斯的随机投影向量
    b：[0, w) 上的均匀偏移
    w：桶宽（>0）

你需要实现 project8 文档第 3 节要求的三个函数（见下方 TODO）：
    build_index(vectors, k, w, seed)
    query(index, query_vector, top_k)
    brute_force(vectors, query_vector, top_k)

约定（project8 验收点）：
    - 空桶返回 []；候选不足 top_k 返回实际数量，绝不偷偷全库扫描。
    - 同距离按 ID 升序固定排序。
    - floor 对负数向下取整：floor(-0.1) = -1，不能用 int() 向零截断。
    - 固定种子时键可复现；所有桶中 ID 总数 = 库大小。

运行（实现完 TODO 后）：
    python3 lsh_basic.py --handcalc    # Q5 手算核对
    python3 lsh_basic.py               # 合成数据演示
    python3 lsh_basic.py --k 2 --w 2.0

没实现就跑会抛 NotImplementedError，不会崩溃。
卡住了看函数注释里的参考答案（取消注释），但建议先自己想 5 分钟。
"""

from __future__ import annotations

import argparse
from typing import Dict, List, Tuple

import numpy as np


# ──────────────────────────────────────────────────────────────────────────
#  index 数据结构约定（build_index 返回、query 读取）
# ──────────────────────────────────────────────────────────────────────────
# index 是一个 dict，字段：
#   "A"        : (k, dim) 投影向量，每行一个 a
#   "B"        : (k,)    偏移，每个一个 b
#   "w"        : float   桶宽
#   "k"        : int     哈希函数个数
#   "dim"      : int     向量维数
#   "N"        : int     库大小
#   "buckets"  : dict，键 = tuple(int, ...)（长度 k），值 = list[int] 库 ID
#   "vectors"  : (N, dim) 原始库向量，供 query 重排时算真实距离
# 用 dict 是因为 E2LSH 的桶号是稀疏的整数元组，字典天然稀疏存储。


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  TODO 1：build_index —— 建一张 E2LSH 表（必做）                       ║
# ╚══════════════════════════════════════════════════════════════════════╝
def build_index(vectors: np.ndarray, k: int, w: float,
                seed: int) -> Dict:
    """建一张 E2LSH 表。

    参数
    ----
    vectors : (N, dim) float64 库向量
    k       : 级联哈希函数个数（Basic 取 1 或 2）
    w       : 桶宽，>0
    seed    : 随机种子

    返回
    ----
    index : 上面注释里约定的 dict。

    提示
    ----
    1. 校验 k>=1、w>0、vectors 是二维。
    2. 用 np.random.default_rng(seed) 建一个 rng（固定种子 → 可复现）。
    3. A = rng.standard_normal((k, dim))   # 各维独立标准高斯
       B = rng.uniform(0.0, w, size=k)     # 偏移 ∈ [0, w)
    4. 对每个向量算键：proj = vectors @ A.T + B      # (N, k)
       keys = np.floor(proj / w).astype(np.int64)   # 注意 floor 负数！
       每个键转成 Python int 元组（tuple(int(v) for v in row)）才能做字典键。
    5. buckets[key].append(i)，遍历所有 i。
    6. 返回上面约定的 dict。

    关键检查：所有桶里 ID 加起来 = N（库大小）。
    """
    # ===== 删掉下面的 raise，换成你的实现 =====
    raise NotImplementedError(
        "TODO 1: 实现 build_index（见函数注释提示）")


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  TODO 2：query —— 同桶候选 + 真实距离重排（必做）                     ║
# ╚══════════════════════════════════════════════════════════════════════╝
def query(index: Dict, query_vector: np.ndarray,
          top_k: int) -> List[Tuple[int, float]]:
    """在已建好的单表索引上查询。

    返回 (id, 欧氏距离) 列表，按 (距离, id) 升序。
    空桶返回 []；候选不足 top_k 返回实际数量，不全库扫描。

    提示
    ----
    1. 算查询键：proj = index["A"] @ q + index["B"]   # (k,)
       key = tuple(int(v) for v in
                   np.floor(proj / index["w"]).astype(np.int64))
    2. candidates = index["buckets"].get(key, [])
       没候选就 return []。
    3. 算真实欧氏距离（开根号）：
       cand_vecs = index["vectors"][candidates]
       diff = cand_vecs - q
       dists = np.sqrt(np.einsum("ij,ij->i", diff, diff))
    4. 排序：sorted(range(len(cand)), key=lambda i: (dists[i], cand_ids[i]))
       —— 同距离按 id 升序（固定 tie-break）。
    5. 取前 min(top_k, len) 个，返回 [(id, dist), ...]。
    """
    # ===== 删掉下面的 raise，换成你的实现 =====
    raise NotImplementedError(
        "TODO 2: 实现 query（见函数注释提示）")


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  TODO 3：brute_force —— 全库精确 top-K（必做）                         ║
# ╚══════════════════════════════════════════════════════════════════════╝
def brute_force(vectors: np.ndarray, query_vector: np.ndarray,
                top_k: int) -> List[Tuple[int, float]]:
    """暴力 top-K：对全库算欧氏距离，按 (距离, id) 升序。

    提示
    ----
    1. diff = vectors - q
       dists = np.sqrt(np.einsum("ij,ij->i", diff, diff))
    2. sorted(range(N), key=lambda i: (dists[i], i))   # 同距离按 id
    3. 取前 min(top_k, N) 个返回 [(id, dist), ...]。
    """
    # ===== 删掉下面的 raise，换成你的实现 =====
    raise NotImplementedError(
        "TODO 3: 实现 brute_force（见函数注释提示）")


# ──────────────────────────────────────────────────────────────────────────
#  下面是已实现的脚手架，不用改：合成数据、Q5 核对、演示、命令行
# ──────────────────────────────────────────────────────────────────────────
def make_data(n: int, dim: int, seed: int) -> np.ndarray:
    """生成 n 个 dim 维向量，固定种子。"""
    rng = np.random.default_rng(seed)
    return rng.standard_normal((n, dim)).astype(np.float64)


def _build_fixed_index(vectors: np.ndarray, A: np.ndarray,
                       B: np.ndarray, w: float) -> Dict:
    """用固定的 A/B/w 直接构造 index（仅供 run_handcalc 核对 Q5 用）。

    不走随机种子，因为 project8 第 4 节的 Q5 固定 a=1, b=0, w=2。
    index 结构必须和 build_index 返回的完全一致（见文件顶部约定）。
    """
    vectors = np.asarray(vectors, dtype=np.float64)
    A = np.asarray(A, dtype=np.float64)
    B = np.asarray(B, dtype=np.float64)
    proj = vectors @ A.T + B
    keys_int = np.floor(proj / w).astype(np.int64)
    buckets: Dict[Tuple[int, ...], List[int]] = {}
    for i in range(len(vectors)):
        key = tuple(int(v) for v in keys_int[i])
        buckets.setdefault(key, []).append(i)
    return {"A": A, "B": B, "w": float(w), "k": int(A.shape[0]),
            "dim": int(vectors.shape[1]), "N": int(len(vectors)),
            "buckets": buckets, "vectors": vectors}


def run_handcalc() -> None:
    """Q5 手算核对（project8 第 4 节）。

    q=1.9, h(x)=floor(x/2)，即 a=1, b=0, w=2, k=1。
    预期：桶 0 = {a, b}；LSH top-1 = b（距离 0.9）；
          暴力 top-1 = c（距离 0.2）；Recall@1 = 0。
    """
    ids = ["a", "b", "c", "d"]
    data = np.array([[0.2], [1.0], [2.1], [4.5]], dtype=np.float64)
    q = np.array([1.9], dtype=np.float64)
    # 固定 a=1, b=0, w=2（手算参数，不用随机种子）
    index = _build_fixed_index(
        data,
        A=np.array([[1.0]]), B=np.array([0.0]), w=2.0)

    print("=" * 60)
    print("Q5 手算核对：q = 1.9, h(x) = floor(x / 2)  (a=1, b=0, w=2)")
    print("=" * 60)
    print(f"{'ID':>4} {'x':>6} {'桶号':>6} {'到q距离':>10} {'同桶候选':>10}")
    qkey = tuple(int(v) for v in
                 np.floor((index["A"] @ q + index["B"]) / index["w"]).astype(np.int64))
    for i, x in enumerate(data[:, 0]):
        key = tuple(int(v) for v in
                    np.floor((index["A"] @ data[i] + index["B"]) / index["w"]).astype(np.int64))
        dist = float(abs(x - q[0]))
        in_bucket = "是" if key == qkey else "否"
        print(f"{ids[i]:>4} {x:>6.1f} {str(key):>6} {dist:>10.1f} {in_bucket:>10}")

    lsh = query(index, q, top_k=1)
    bf = brute_force(data, q, top_k=1)

    print()
    print(f"查询 q 的桶号: {qkey}  → 同桶候选 ID: "
          f"{[ids[c] for c in index['buckets'].get(qkey, [])]}")
    print(f"暴力 top-1: {ids[bf[0][0]]} (距离 {bf[0][1]:.1f})  ← 真实最近邻")
    if lsh:
        print(f"LSH  top-1: {ids[lsh[0][0]]} (距离 {lsh[0][1]:.1f})  "
              "← 同桶最近邻")
    else:
        print("LSH  top-1: (空桶)")
    hit = bool(lsh) and lsh[0][0] == bf[0][0]
    recall = 1.0 if hit else 0.0
    print(f"Recall@1 = {recall:.0f}  "
          f"({'命中' if hit else '漏检：c 没进候选，精确重排无法找回'})")


def run_demo(n: int, dim: int, k: int, w: float, top_k: int,
             seed: int, self_query: bool) -> None:
    print("=" * 60)
    print(f"合成数据演示：N={n}, dim={dim}, k={k}, w={w}, "
          f"top_k={top_k}, seed={seed}")
    print("=" * 60)

    data = make_data(n, dim, seed)
    rng = np.random.default_rng(seed + 1)
    if self_query:
        queries = data[:5].copy()
        qids = list(range(5))
    else:
        queries = rng.standard_normal((5, dim))
        qids = [-1] * 5

    import time
    t0 = time.perf_counter()
    index = build_index(data, k=k, w=w, seed=seed)
    t1 = time.perf_counter()
    print(f"建表耗时: {(t1 - t0) * 1000:.2f} ms")
    print(f"桶数: {len(index['buckets'])}；"
          f"桶中 ID 总数: {sum(len(v) for v in index['buckets'].values())} "
          f"（应等于 N={n}）")

    recalls = []
    cand_counts = []
    miss_examples = []
    print(f"\n{'q#':>3} {'桶候选':>8} {'返回':>6} {'Recall@K':>9}  说明")
    for qi, q in enumerate(queries):
        bf = brute_force(data, q, top_k=top_k)
        lsh = query(index, q, top_k=top_k)
        # 真实候选数 = 同桶 ID 数（未按 top_k 截断）
        qkey = tuple(int(v) for v in
                     np.floor((index["A"] @ q + index["B"]) / index["w"]).astype(np.int64))
        raw_cand = len(index["buckets"].get(qkey, []))
        gt = set(i for i, _ in bf)
        got = set(i for i, _ in lsh)
        recall = len(gt & got) / top_k
        recalls.append(recall)
        cand_counts.append(raw_cand)
        note = ""
        if recall < 1.0:
            missing = gt - got
            note = (f"漏检 ID {sorted(missing)}（未进同桶）"
                    if missing else "候选不足K")
            if len(miss_examples) < 3:
                miss_examples.append((qi, sorted(missing), note))
        print(f"{qi:>3} {raw_cand:>8} {len(lsh):>6} {recall:>9.2f}  {note}")

    print(f"\n平均 Recall@{top_k}: {np.mean(recalls):.3f}")
    print(f"平均候选数: {np.mean(cand_counts):.1f} / 库大小 {n}")
    if miss_examples:
        print("\n漏检样例（解释原因）:")
        for qi, missing, note in miss_examples:
            print(f"  查询 {qi}: {note}")


def main() -> None:
    p = argparse.ArgumentParser(description="LSH 基础版：单表 E2LSH 检索（学生版）")
    p.add_argument("--handcalc", action="store_true",
                   help="只跑 Q5 一维手算例子")
    p.add_argument("--n", type=int, default=500, help="库向量数（100-1000）")
    p.add_argument("--dim", type=int, default=2, help="向量维数")
    p.add_argument("--k", type=int, default=1, help="单表哈希函数个数（1 或 2）")
    p.add_argument("--w", type=float, default=2.0, help="桶宽")
    p.add_argument("--topk", type=int, default=5, help="返回近邻数")
    p.add_argument("--seed", type=int, default=42, help="随机种子")
    p.add_argument("--self-query", action="store_true",
                   help="用库向量自己当查询（含自己，用于核对）")
    args = p.parse_args()

    if args.handcalc:
        run_handcalc()
        return
    run_demo(n=args.n, dim=args.dim, k=args.k, w=args.w,
             top_k=args.topk, seed=args.seed, self_query=args.self_query)
    print("\n--- 还可以单独跑 Q5 手算核对 ---")
    print("python3 lsh_basic.py --handcalc")


if __name__ == "__main__":
    main()
