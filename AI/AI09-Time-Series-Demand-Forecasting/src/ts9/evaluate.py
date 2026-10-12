"""场景分组评价（Advance 可选增强，Basic 不需要改动）。

对应 G5：在同一批小时上比较不同方法的总体与分场景误差、覆盖率与区间宽度。
覆盖率是落在区间内的目标比例；宽度是上界减下界。所有方法用相同暖启动与缺失剔除。

TODO（Advance）：定义高峰/低谷、工作日/周末、天气与测试前七天等分组；
实测天气可用于事后分组，但不能作为预测输入。每组都要报告组大小。
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np


def coverage_width(
    y_true: List[float],
    y_pred: List[float],
    lower: List[float],
    upper: List[float],
) -> Dict[str, float]:
    """给定点预测与区间上下界，返回覆盖率与平均宽度。"""
    t = np.asarray(y_true, dtype=float)
    p = np.asarray(y_pred, dtype=float)
    lo = np.asarray(lower, dtype=float)
    hi = np.asarray(upper, dtype=float)
    inside = np.sum((t >= lo) & (t <= hi))
    return {
        "coverage": float(inside) / len(t) if len(t) else float("nan"),
        "mean_width": float(np.mean(hi - lo)) if len(t) else float("nan"),
    }


def group_metrics(
    y_true: List[float],
    y_pred: List[float],
    groups: List[str],
) -> Dict[str, Dict[str, float]]:
    """按分组名列表（与 y 等长）返回各组 MAE / RMSE / 样本数。"""
    out: Dict[str, Dict[str, float]] = {}
    arr_t = np.asarray(y_true, dtype=float)
    arr_p = np.asarray(y_pred, dtype=float)
    for g in set(groups):
        idx = [i for i, x in enumerate(groups) if x == g]
        if not idx:
            continue
        err = np.abs(arr_t[idx] - arr_p[idx])
        sq = (arr_t[idx] - arr_p[idx]) ** 2
        out[g] = {
            "mae": float(np.mean(err)),
            "rmse": float(np.sqrt(np.mean(sq))),
            "n": float(len(idx)),
        }
    return out


__all__ = ["coverage_width", "group_metrics"]
