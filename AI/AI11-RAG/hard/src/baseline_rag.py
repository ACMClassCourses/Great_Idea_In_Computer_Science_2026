"""baseline_rag.py — 普通 RAG 流程（TODO 1–2）。

复用同级 `basic/src/rag11` 的检索与生成，对每道题产出 answer 与 citation_ids。
对应 Hard 任务中的 Baseline RAG 流程。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASIC_ROOT = ROOT.parent / "basic"
sys.path.insert(0, str(BASIC_ROOT / "src"))

from utils import load_jsonl, save_jsonl, load_documents  # noqa: E402


def run_baseline(questions: list[dict], docs: list, config: dict) -> list[dict]:
    """TODO 1–2：对每道题检索 top-k、生成带引用回答，返回 responses。

    使用 rag11.retriever.Retriever(chunks=docs) 与 rag11.generator.generate，确保与
    Evidence-bound 流程使用完全相同的检索结果与模型配置。
    """
    raise NotImplementedError("TODO 1–2: 实现 Baseline RAG（检索 + 生成 + 引用）")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data")
    ap.add_argument("--output", default="outputs/baseline.jsonl")
    ap.add_argument("--config", default=str(ROOT / "configs" / "default.yaml"))
    args = ap.parse_args()

    import yaml
    from rag11 import generator, retriever

    config = yaml.safe_load(open(args.config, encoding="utf-8"))
    questions = load_jsonl(Path(args.data) / "questions.jsonl")
    docs = load_documents(Path(args.data) / "documents.jsonl")

    responses = run_baseline(questions, docs, config)  # TODO 1–2
    save_jsonl(ROOT / args.output, responses)
    print(f"Baseline 产出 {len(responses)} 条回答 -> {ROOT / args.output}")


if __name__ == "__main__":
    main()
