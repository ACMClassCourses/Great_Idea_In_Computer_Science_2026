"""Advance 公共工具：jsonl 读写与场景分组辅助（已提供，无需修改）。"""

from __future__ import annotations

import json
import os
from typing import Dict, List

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 把上级 src 加入路径，便于复用 Basic 的三基线与指标
import sys  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "src"))


def read_jsonl(path: str) -> List[dict]:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path: str, rows: List[dict]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def classify_scenario(ts, value, peak_hours=(7, 9, 17, 19)) -> Dict[str, str]:
    """把一行目标小时分到场景（事后分析用，不影响预测）。

    - weekday / weekend：由星期几决定（日历可提前知道）
    - peak / offpeak：由小时是否落在高峰区间决定（日历可提前知道）
    - 实测天气（如传入）只能事后分组，不能作为预测输入
    """
    hour = ts.hour
    dow = ts.dayofweek
    return {
        "weekday_weekend": "weekend" if dow >= 5 else "weekday",
        "peak_offpeak": "peak" if hour in peak_hours else "offpeak",
    }


__all__ = ["read_jsonl", "write_jsonl", "classify_scenario", "ROOT"]
