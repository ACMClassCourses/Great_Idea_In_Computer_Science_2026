"""00_self_check.py — Basic 组件自检（对应 README Basic TODO 1–7）。

运行：python examples/00_self_check.py
把 src/rag11 加入路径后逐一对未完成的 TODO 报告状态；已实现的部分会真正执行。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _status(name: str, fn) -> None:
    try:
        fn()
        print(f"[PASS] {name}")
    except NotImplementedError as e:
        print(f"[TODO] {name}: {e}")
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] {name}: {type(e).__name__}: {e}")


def main() -> None:
    from rag11 import ingest, bm25, retriever, prompts, generator

    def t_ingest() -> None:
        chunks = ingest.load_corpus(ROOT / "data" / "demo")
        assert chunks, "load_corpus 返回为空"

    def t_bm25() -> None:
        chunks = ingest.load_corpus(ROOT / "data" / "demo")
        model = bm25.BM25().fit(chunks)
        res = model.search("北河馆 周一 开放", k=3)
        assert res, "BM25.search 返回为空"

    def t_retriever() -> None:
        r = retriever.Retriever(corpus_dir=str(ROOT / "data" / "demo"), mode="sparse")
        top = r.retrieve("北河馆 周一 开放", k=3)
        assert top, "retriever.sparse 返回为空"

    def t_prompt() -> None:
        p = prompts.build_prompt("示例问题？", ["示例证据片段。"])
        assert "[1]" in p

    def t_generator() -> None:
        # TODO 6 完成后改为真实 backend
        raise NotImplementedError("TODO 6: 真实 LLM 生成尚未实现（可用 stub 临时打通）")

    print("== Basic 自检 ==")
    _status("TODO 1 load_corpus/chunk", t_ingest)
    _status("TODO 2 BM25.fit/search", t_bm25)
    _status("TODO 5 retriever.sparse", t_retriever)
    _status("prompts.build", t_prompt)
    _status("TODO 6 generator", t_generator)
    print("\n完成。PASS 表示已实现；TODO 表示待补全；FAIL 表示实现有 bug。")


if __name__ == "__main__":
    main()
