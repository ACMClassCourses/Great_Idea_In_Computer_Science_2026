"""01_build_index.py — 建索引（对应 Basic 流程演示）。

运行：python examples/01_build_index.py --config configs/default.yaml
把语料切分、构建检索器，并把 chunk 元信息保存到 outputs/index.json。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs" / "default.yaml"))
    ap.add_argument("--corpus", default=None)
    ap.add_argument("--top-k", type=int, default=None)
    args = ap.parse_args()

    import yaml
    import yaml  # noqa
    from rag11 import ingest, retriever

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    corpus = args.corpus or config["paths"]["corpus"]
    top_k = args.top_k or config["retrieval"]["top_k"]

    chunks = ingest.load_corpus(ROOT / corpus)
    r = retriever.Retriever(chunks=chunks, mode=config["retrieval"]["mode"], top_k=top_k)

    out = ROOT / config["paths"]["index"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {"mode": r.mode, "top_k": top_k, "n_chunks": len(chunks),
             "chunks": [{"id": c.id, "source": c.source, "text": c.text} for c in chunks]},
            ensure_ascii=False, indent=2,
        ),
        encoding="utf-8",
    )
    print(f"已建索引：{len(chunks)} 个块，模式={r.mode}，保存到 {out}")


if __name__ == "__main__":
    main()
