"""指标：MAE / RMSE / WAPE（从零实现，不调库）。

设计边界：
- 全部按"逐小时点预测 vs 真值"的成对序列计算。
- WAPE 的分母是真值绝对值之和；当分母为 0（所有真值都是 0）时返回 ``None``，
  避免除以零，也避免给 MAPE/WAPE 编造一个值。
- 单个样本点（如真值为 0 的小时）不能算 MAPE，但其绝对误差仍计入 MAE/RMSE/WAPE
  的分母，所以 Q5 中第三行（真值 0）照常参与汇总。

参考 README 第 4 节 Q5 手算：
    真值 [10,20,0,30]  预测 [12,18,5,25]
    MAE  = 14/4 = 3.5
    RMSE = sqrt(58/4) ≈ 3.8079
    WAPE = 14/60 ≈ 23.33%
"""

from __future__ import annotations

from typing import Iterable, List, Optional

import numpy as np


def _as_array(values: Iterable[float]) -> np.ndarray:
    arr = np.asarray(list(values), dtype=float)
    if arr.ndim != 1:
        raise ValueError("metrics 输入必须是一维成对序列")
    return arr


def mae(y_true: Iterable[float], y_pred: Iterable[float]) -> float:
    """平均绝对误差。实现提示：mean(|t - p|)；长度不齐抛错；空序列返回 nan。"""
    raise NotImplementedError("TODO 5：实现 MAE = mean(|y_true - y_pred|)。")


def rmse(y_true: Iterable[float], y_pred: Iterable[float]) -> float:
    """均方根误差。实现提示：sqrt(mean((t - p)^2))；长度不齐抛错；空序列返回 nan。"""
    raise NotImplementedError("TODO 5：实现 RMSE = sqrt(mean((y_true - y_pred)^2))。")


def wape(y_true: Iterable[float], y_pred: Iterable[float]) -> Optional[float]:
    """加权绝对百分比误差 = 总绝对误差 / 真值绝对值之和。

    真值之和为 0 时返回 None（不能除以零，也不可编造）。
    """
    raise NotImplementedError(
        "TODO 5：实现 WAPE = sum(|t - p|) / sum(|t|)；sum(|t|)==0 时返回 None。"
    )


def evaluate(
    y_true: Iterable[float], y_pred: Iterable[float]
) -> dict:
    """一次性给出三项指标，便于演示与自检。

    返回键：mae / rmse / wape（wape 可能为 None）。
    """
    return {
        "mae": mae(y_true, y_pred),
        "rmse": rmse(y_true, y_pred),
        "wape": wape(y_true, y_pred),
        "n": len(list(y_true)),
    }


# 暴露一个便于 `from ts9.metrics import *` 的清单
__all__: List[str] = ["mae", "rmse", "wape", "evaluate"]
