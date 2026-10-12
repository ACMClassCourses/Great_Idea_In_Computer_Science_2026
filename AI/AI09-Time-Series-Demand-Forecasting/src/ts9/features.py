"""特征构造（Advance 可选增强，Basic 不需要改动）。

提供"只使用过去"的滞后 / 日历特征构造，配套 G1（特征可得性表）与 G3（特征模型）。
所有统计量都先移位再滚动，防止把目标真值混入均值。

TODO（Advance）：选一个模型（岭回归 / 随机森林 / HGB）在 train 上拟合，
并在 dev 上用滚动起点选择少量配置；不要在此文件里做随机切分。
"""

from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd


def build_features(
    df: pd.DataFrame,
    lags: List[int],
    datetime_col: str = "timestamp",
    value_col: str = "value",
) -> pd.DataFrame:
    """为每个目标小时构造"仅来自过去"的特征。

    - 滞后特征：value 在 t-lag 小时的值（来自历史，不偷看未来）。
    - 日历特征：小时、星期几、是否周末（这些在目标时刻可提前知道）。
    返回带特征列与对齐 ``value`` 作为 y 的 DataFrame；首部无法构造滞后处被丢弃。
    """
    out = df[[datetime_col, value_col]].copy()
    out["hour"] = out[datetime_col].dt.hour
    out["dow"] = out[datetime_col].dt.dayofweek
    out["is_weekend"] = (out["dow"] >= 5).astype(int)
    for lag in lags:
        out[f"lag_{lag}"] = out[value_col].shift(lag)
    out = out.dropna().reset_index(drop=True)
    return out


def feature_matrix(
    feats: pd.DataFrame,
    lag_cols: List[int],
) -> tuple:
    """返回 (X, y)。X 包含滞后列 + 日历列。"""
    feature_cols = [f"lag_{l}" for l in lag_cols] + ["hour", "dow", "is_weekend"]
    X = feats[feature_cols].to_numpy(dtype=float)
    y = feats["value"].to_numpy(dtype=float)
    return X, y


__all__ = ["build_features", "feature_matrix"]
