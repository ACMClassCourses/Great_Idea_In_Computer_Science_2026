"""check.py —— 自测脚本（完整提供，随时运行）

    python src/check.py

每完成一个任务就运行一次。所有正确性用例都可以手工复核
（见 docs/implement_guide.md 第 6 节），测试失败时请先自己手算一遍。

三个任务的测试互相独立：任务一没做完不影响验证任务二、三。
"""
import sys
from pathlib import Path

# 让 Windows 老式终端也能正常显示
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent))

from graph import is_valid_coloring, random_graph  # noqa: E402

DATA = Path(__file__).resolve().parent.parent / "data"

results = []  # (名称, 状态, 备注)；状态 ∈ {"pass", "fail", "todo"}


def report(name, status, note=""):
    results.append((name, status, note))
    icon = {"pass": "✅ 通过", "fail": "❌ 失败", "todo": "⏳ 未完成"}[status]
    line = f"[{icon}] {name}"
    if note:
        line += f" —— {note}"
    print(line)


def make_cycle(n):
    adj = [set() for _ in range(n)]
    for i in range(n):
        adj[i].add((i + 1) % n)
        adj[(i + 1) % n].add(i)
    return adj


def make_complete(n):
    return [set(range(n)) - {i} for i in range(n)]


# ---------------------------------------------------------------- 任务一
def check_two_color():
    name = "任务一：two_color 二染色（二分图判定）"
    try:
        from solver import two_color
    except NotImplementedError as e:
        report(name, "todo", str(e))
        return
    try:
        # 四元环：二分图，可二染色
        r = two_color(4, make_cycle(4))
        assert r is not None, "四元环是二分图，应返回染色方案而不是 None"
        assert is_valid_coloring(4, make_cycle(4), r, num_colors=2), f"四元环的染色方案不合法：{r}"

        # 三角形：奇环，不可二染色
        assert two_color(3, make_cycle(3)) is None, "三角形是奇环，不可二染色，应返回 None"

        # 不连通图：三角形 + 孤立边，整体不可二染色
        adj = make_cycle(3) + [set(), set()]
        adj[3].add(4); adj[4].add(3)
        assert two_color(5, adj) is None, "含三角形的不连通图不可二染色（检查是否只搜了第一个连通分量）"

        # 不连通的可染图：四元环 + 孤立顶点
        adj2 = make_cycle(4) + [set()]
        r = two_color(5, adj2)
        assert r is not None and is_valid_coloring(5, adj2, r, num_colors=2), \
            "四元环加孤立顶点应当可二染色（孤立顶点也要染色）"
    except NotImplementedError as e:
        report(name, "todo", str(e))
        return
    except AssertionError as e:
        report(name, "fail", str(e))
        return
    report(name, "pass")


# ---------------------------------------------------------------- 任务二
def check_backtrack():
    name = "任务二：three_color_backtrack 朴素回溯"
    try:
        from solver import three_color_backtrack
    except NotImplementedError as e:
        report(name, "todo", str(e))
        return
    try:
        # 三角形：可三染色，方案必须合法
        st = {"nodes": 0}
        r = three_color_backtrack(3, make_cycle(3), st)
        assert r is not None, "三角形可三染色，不应返回 None"
        assert is_valid_coloring(3, make_cycle(3), r), f"三角形的染色方案不合法：{r}"
        assert st["nodes"] > 0, "stats['nodes'] 没有自增——性能实验全靠它，见 docs 第 3.4 节"

        # K4：不可三染色
        st = {"nodes": 0}
        assert three_color_backtrack(4, make_complete(4), st) is None, \
            "K4 需要 4 种颜色，三染色应返回 None（是不是提前返回或漏了回溯？）"

        # Petersen 图：可三染色的非平凡实例（从 data/ 读入，顺便验证文件格式）
        from graph import load_graph
        n, adj = load_graph(DATA / "petersen.txt")
        st = {"nodes": 0}
        r = three_color_backtrack(n, adj, st)
        assert r is not None and is_valid_coloring(n, adj, r), "Petersen 图应当可三染色"
    except NotImplementedError as e:
        report(name, "todo", str(e))
        return
    except AssertionError as e:
        report(name, "fail", str(e))
        return
    report(name, "pass")


# ---------------------------------------------------------------- Advance C1
def check_mrv():
    name = "Advance C1：three_color_mrv 启发式与前向检查"
    try:
        from solver import three_color_backtrack, three_color_mrv
    except NotImplementedError as e:
        report(name, "todo", str(e))
        return
    try:
        from graph import load_graph

        # 正确性：Petersen 可染、Grötzsch 图不可染
        n, adj = load_graph(DATA / "petersen.txt")
        st = {"nodes": 0}
        r = three_color_mrv(n, adj, st, forward_check=True)
        assert r is not None and is_valid_coloring(n, adj, r), "Petersen 图应当可三染色"

        n2, adj2 = load_graph(DATA / "mycielski4.txt")
        st = {"nodes": 0}
        assert three_color_mrv(n2, adj2, st, forward_check=True) is None, \
            "Grötzsch 图（无三角形！）需要 4 色，应返回 None"

        # 性能：同一实例上 MRV+前向检查的节点数必须显著少于朴素回溯
        n3, adj3 = random_graph(24, 48, seed=2)
        st_naive = {"nodes": 0}
        r_naive = three_color_backtrack(n3, adj3, st_naive)
        st_mrv = {"nodes": 0}
        r_mrv = three_color_mrv(n3, adj3, st_mrv, forward_check=True)
        assert (r_naive is None) == (r_mrv is None), "两个求解器结论不一致，必然有一个有 bug"
        assert st_mrv["nodes"] < st_naive["nodes"], \
            f"MRV+前向检查（{st_mrv['nodes']} 节点）应少于朴素回溯（{st_naive['nodes']} 节点）"
        note = f"该实例上：朴素 {st_naive['nodes']} 节点 → MRV+FC {st_mrv['nodes']} 节点"
    except NotImplementedError as e:
        report(name, "todo", str(e))
        return
    except AssertionError as e:
        report(name, "fail", str(e))
        return
    report(name, "pass", note)


def main():
    print("=" * 60)
    print("三染色项目自测")
    print("=" * 60)
    check_two_color()
    check_backtrack()
    check_mrv()

    print("-" * 60)
    n_pass = sum(1 for _, s, _ in results if s == "pass")
    if n_pass == len(results):
        print(f"全部 {n_pass}/{len(results)} 项通过！可以做性能对比实验了：")
        print("    python src/main.py bench")
        sys.exit(0)
    else:
        print(f"当前进度 {n_pass}/{len(results)}。失败/未完成的项请对照 docs/implement_guide.md 调试。")
        sys.exit(1)


if __name__ == "__main__":
    main()
