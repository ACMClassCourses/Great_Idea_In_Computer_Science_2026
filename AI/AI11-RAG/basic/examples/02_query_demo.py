"""02_query_demo.py — 单条问答演示（对应 Basic TODO 7，端到端串联）。

运行：python examples/02_query_demo.py --question "北河馆周一开放吗？"
输出：问题、命中的 top-k 块、最终回答与引用编号。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--question", default="北河馆周一开放吗？")
    ap.add_argument("--config", default=str(ROOT / "configs" / "default.yaml"))
    ap.add_argument("--corpus", default=None)
    ap.add_argument("--top-k", type=int, default=None)
    args = ap.parse_args()

    import yaml
    from rag11 import generator, ingest, prompts, retriever

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    corpus = args.corpus or config["paths"]["corpus"]
    top_k = args.top_k or config["retrieval"]["top_k"]

    chunks = ingest.load_corpus(ROOT / corpus)
    r = retriever.Retriever(chunks=chunks, mode=config["retrieval"]["mode"], top_k=top_k)
    top = r.retrieve(args.question, top_k)

    print("== 问题 ==")
    print(args.question)
    print("\n== 命中的 top-k 块 ==")
    for rank, (c, score) in enumerate(top, 1):
        print(f"[{rank}] (id={c.id}, score={score:.4f}) {c.text[:80]}...")

    contexts = [c.text for c, _ in top]
    prompt = prompts.build_prompt(args.question, contexts)
    answer, citation_ids = generator.generate(prompt, backend="stub")  # TODO 6 改为真实 backend

    print("\n== 回答 ==")
    print(answer)
    print("\n== 引用编号 ==")
    print(citation_ids)


if __name__ == "__main__":
    main()
