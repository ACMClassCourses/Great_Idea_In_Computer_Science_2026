"""graph.py —— 图的表示、读写与生成（完整提供，可直接使用）

图用邻接表表示：adj[v] 是顶点 v 的邻居集合（set[int]），顶点编号 0..n-1。

图文件格式（UTF-8 文本）：
    # 以井号开头的是注释
    5 4       <- 顶点数 n、边数 m
    0 1       <- 接下来 m 行，每行一条边（无向）
    1 2
    ...
"""
import random
from pathlib import Path


def load_graph(path):
    """从文件读图，返回 (n, adj)。"""
    n, adj = None, None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if n is None:
            n, m = map(int, line.split())
            adj = [set() for _ in range(n)]
        else:
            u, v = map(int, line.split())
            adj[u].add(v)
            adj[v].add(u)
    if n is None:
        raise ValueError(f"图文件为空：{path}")
    return n, adj


def save_graph(path, n, adj, comment=""):
    """把图写入文件。"""
    edges = [(u, v) for u in range(n) for v in adj[u] if u < v]
    lines = [f"# {comment}"] if comment else []
    lines.append(f"{n} {len(edges)}")
    lines += [f"{u} {v}" for u, v in sorted(edges)]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def random_graph(n, m, seed=None):
    """生成恰好 m 条边的随机图（顶点 0..n-1），返回 (n, adj)。相同 seed 结果相同。"""
    rng = random.Random(seed)
    all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    m = min(m, len(all_edges))
    adj = [set() for _ in range(n)]
    for u, v in rng.sample(all_edges, m):
        adj[u].add(v)
        adj[v].add(u)
    return n, adj


def grid_graph(rows, cols):
    """生成 rows×cols 的网格图（每个格子与上下左右相邻），返回 (n, adj)。

    网格图是二分图——想想为什么？（提示：把 (行+列) 的奇偶性当作颜色）
    """
    n = rows * cols
    adj = [set() for _ in range(n)]
    for r in range(rows):
        for c in range(cols):
            v = r * cols + c
            if r + 1 < rows:
                adj[v].add(v + cols)
                adj[v + cols].add(v)
            if c + 1 < cols:
                adj[v].add(v + 1)
                adj[v + 1].add(v)
    return n, adj


def is_valid_coloring(n, adj, coloring, num_colors=3):
    """验证一个染色方案是否合法（完整提供）。

    合法 = 每个顶点都有颜色、颜色在 [0, num_colors) 内、每条边两端颜色不同。
    """
    if coloring is None or len(coloring) != n:
        return False
    if any(c is None or not (0 <= c < num_colors) for c in coloring):
        return False
    return all(coloring[u] != coloring[v] for u in range(n) for v in adj[u] if u < v)


def describe(n, adj):
    """打印图的基本统计。"""
    m = sum(len(s) for s in adj) // 2
    degrees = [len(s) for s in adj]
    print(f"顶点数 n = {n}，边数 m = {m}，平均度数 = {2 * m / max(n, 1):.2f}，"
          f"最大度数 = {max(degrees, default=0)}")
