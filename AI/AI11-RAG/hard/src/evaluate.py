"""evaluate.py — 指标与失败案例（TODO 6–7）。

按根 README §4 的指标定义计算，分母显式写出；导出逐题结果、失败案例与
accuracy–support 二维图。对应根 README Advance 的 G4/G5。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASIC_ROOT = ROOT.parent / "basic"
sys.path.insert(0, str(BASIC_ROOT / "src"))

from utils import load_jsonl  # noqa: E402


def compute_metrics(baseline: list[dict], evidence_bound: list[dict],
                    annotations: list[dict]) -> dict:
    """TODO 6：按根 README 定义计算各项指标，分母显式写出。

    返回包含 accuracy / citation support rate / unsupported claim rate /
    coverage / abstention / 成本 等字段的字典；分母为 0 时记 N/A 而非 100%。
    """
    raise NotImplementedError("TODO 6: 实现指标计算（明确分母）")


def collect_failure_cases(baseline: list[dict], evidence_bound: list[dict]) -> list[dict]:
    """TODO 7：至少覆盖 5 类失败（检索缺失、命中未用、引用相反、无证据扩写、过度拒答）。"""
    raise NotImplementedError("TODO 7: 收集失败案例")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", default="outputs/baseline.jsonl")
    ap.add_argument("--evidence-bound", default="outputs/evidence_bound.jsonl")
    ap.add_argument("--annotations", default="data/annotations.jsonl")
    ap.add_argument("--output", default="outputs/report.md")
    args = ap.parse_args()

    baseline = load_jsonl(ROOT / args.baseline)
    eb = load_jsonl(ROOT / args.evidence_bound)
    ann = load_jsonl(ROOT / args.annotations)

    metrics = compute_metrics(baseline, eb, ann)        # TODO 6
    failures = collect_failure_cases(baseline, eb)        # TODO 7

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "# RAG 忠实度评测报告\n\n"
        f"## 指标\n\n{metrics}\n\n"
        f"## 失败案例（{len(failures)}）\n\n{failures}\n",
        encoding="utf-8",
    )
    print(f"评测报告 -> {out}")


if __name__ == "__main__":
    main()
