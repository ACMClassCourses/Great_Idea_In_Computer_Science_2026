"""evidence_bound.py — 断言-证据绑定流程（TODO 3–5）。

在 Baseline 相同检索结果之上，先把回答拆成原子断言，再为每条断言绑定证据并
判定标签，最后对无依据断言执行保留/改写/拒答。对应 Hard 任务中的 Evidence-bound RAG。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASIC_ROOT = ROOT.parent / "basic"
sys.path.insert(0, str(BASIC_ROOT / "src"))

from utils import load_jsonl, save_jsonl, split_claims, validate_label, load_documents  # noqa: E402


def bind_claims(answer: str, contexts: list[str]) -> list[dict]:
    """TODO 3–5：拆断言 + 绑证据 + 判标签 + 处理无依据。

    返回每条断言的:
      {"claim_id", "claim", "evidence_ids", "label", "action"}
    action ∈ {keep, revise, abstain}。每条保留/改写断言的证据必须来自当前检索结果。
    """
    raise NotImplementedError("TODO 3–5: 实现断言拆分、证据绑定与拒答")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data")
    ap.add_argument("--output", default="outputs/evidence_bound.jsonl")
    ap.add_argument("--baseline", default="outputs/baseline.jsonl")
    ap.add_argument("--config", default=str(ROOT / "configs" / "default.yaml"))
    args = ap.parse_args()

    import yaml
    from rag11 import retriever

    config = yaml.safe_load(open(args.config, encoding="utf-8"))
    top_k = config["retrieval"]["top_k"]
    questions = load_jsonl(Path(args.data) / "questions.jsonl")
    docs = load_documents(Path(args.data) / "documents.jsonl")

    # 使用与 Baseline 完全相同的语料与检索配置，保证检索结果一致
    r = retriever.Retriever(chunks=docs, mode=config["retrieval"]["mode"], top_k=top_k)

    # 读取 Baseline 产出，复用其回答做“断言-证据绑定”
    baseline = {row["question_id"]: row for row in load_jsonl(ROOT / args.baseline)}

    rows: list[dict] = []
    for q in questions:
        top = r.retrieve(q["question"], top_k)
        contexts = [c.text for c, _ in top]
        base = baseline.get(q["id"])
        answer = base["answer"] if base else ""   # 复用 Baseline 回答
        # TODO 3–5：拆断言 + 绑证据 + 判标签 + 处理无依据
        claims = bind_claims(answer, contexts)
        rows.append({"question_id": q["id"], "answer": answer, "claims": claims})
    save_jsonl(ROOT / args.output, rows)
    print(f"Evidence-bound 产出 {len(rows)} 题断言 -> {ROOT / args.output}")


if __name__ == "__main__":
    main()
