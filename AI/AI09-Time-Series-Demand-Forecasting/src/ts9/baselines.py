"""三个点预测基线（Basic TODO 3–4，从零实现，不调库）。

TODO 3：从零实现
    - ``NaiveForecaster``          前 1 小时
    - ``SeasonalNaiveForecaster(lag)``  前 24 / 168 小时（日 / 周同小时）
    - ``RollingMeanForecaster(window)``  预测前 ``window`` 小时均值
TODO 4：按时间戳寻找历史值，缺失时回退到可用过去均值或标记不可评价；
        **不得用未来插值**（任何 t 的预测只能使用 timestamp < t 的历史）。

预测协议（与 README A 节一致）：
- ``forecast(test_df, history_df)`` 对 test 中每个目标小时 t 给出点预测。
- ``history_df`` 必须严格早于 test（通常用 train+dev），因此不会偷看未来。
- 若所需历史时间戳缺失，则回退为 history 的全局均值；若该目标本身缺失值则标记
  为 ``None``（不可评价），不参与指标计算。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


def _history_lookup(history: pd.DataFrame) -> Dict[pd.Timestamp, float]:
    """把历史序列做成 {timestamp: value} 查表，便于按滞后定位。"""
    return dict(zip(history["timestamp"], history["value"]))


class BaseForecaster(ABC):
    """所有基线的统一接口。"""

    def __init__(self) -> None:
        self._hist: Optional[pd.DataFrame] = None
        self._lut: Dict[pd.Timestamp, float] = {}
        self._mean: float = float("nan")

    def fit(self, history: pd.DataFrame) -> "BaseForecaster":
        """记录历史序列（严格早于预测时刻的数据）。"""
        self._hist = history.reset_index(drop=True)
        self._lut = _history_lookup(self._hist)
        self._mean = float(np.mean(self._hist["value"].to_numpy()))
        return self

    @abstractmethod
    def _predict_one(self, t: pd.Timestamp) -> Optional[float]:
        """给定目标时刻 t，返回点预测；不可评价返回 None。"""

    def forecast(
        self, test_df: pd.DataFrame
    ) -> List[Tuple[pd.Timestamp, float, Optional[float]]]:
        """对 test 每个目标小时产出 (timestamp, y_true, y_pred)。"""
        if self._hist is None:
            raise RuntimeError("请先调用 fit(history)")
        out: List[Tuple[pd.Timestamp, float, Optional[float]]] = []
        for _, row in test_df.iterrows():
            t = row["timestamp"]
            if t <= self._hist["timestamp"].iloc[-1]:
                # 防御：目标时刻不应落在历史之内（会偷看未来）
                raise ValueError(f"目标时刻 {t} 不晚于历史末端，违反时间协议")
            y_true = float(row["value"])
            y_pred = self._predict_one(t)
            out.append((t, y_true, y_pred))
        return out


class NaiveForecaster(BaseForecaster):
    """前 1 小时的值作为预测（无训练参数）。"""

    def _predict_one(self, t: pd.Timestamp) -> Optional[float]:
        # TODO 3：用 t 之前 1 小时的历史值预测；若缺失则回退 self._mean。
        raise NotImplementedError(
            "TODO 3：NaiveForecaster 用 t-1h 的历史值；缺失时回退 self._mean。"
        )


class SeasonalNaiveForecaster(BaseForecaster):
    """前 ``lag`` 小时的值作为预测；lag=24 为日同小时，lag=168 为周同小时。"""

    def __init__(self, lag: int = 24) -> None:
        super().__init__()
        if lag <= 0:
            raise ValueError("lag 必须为正整数小时")
        self.lag = int(lag)

    def _predict_one(self, t: pd.Timestamp) -> Optional[float]:
        # TODO 3–4：用 t 之前 lag 小时的历史值预测；缺失则回退 self._mean。
        raise NotImplementedError(
            "TODO 3–4：SeasonalNaiveForecaster 用 t-lag 小时的历史值；缺失回退 self._mean。"
        )


class RollingMeanForecaster(BaseForecaster):
    """预测前 ``window`` 个**可用**小时的平均值。"""

    def __init__(self, window: int = 24) -> None:
        super().__init__()
        if window <= 0:
            raise ValueError("window 必须为正整数")
        self.window = int(window)

    def _predict_one(self, t: pd.Timestamp) -> Optional[float]:
        # TODO 3–4：取严格早于 t 的最近 window 个历史值求均值；无历史则回退 self._mean。
        raise NotImplementedError(
            "TODO 3–4：RollingMeanForecaster 取 t 之前最近 window 个历史值求均值；"
            "无历史则回退 self._mean。"
        )


def run_all_baselines(
    history: pd.DataFrame,
    test_df: pd.DataFrame,
    season_lags: Tuple[int, int] = (24, 168),
    rolling_window: int = 24,
) -> Dict[str, List[Tuple[pd.Timestamp, float, Optional[float]]]]:
    """一次跑完三基线（或更多），返回 {name: forecast结果}。"""
    builders = {
        "naive": lambda: NaiveForecaster(),
        "seasonal_24": lambda: SeasonalNaiveForecaster(season_lags[0]),
        "seasonal_168": lambda: SeasonalNaiveForecaster(season_lags[1]),
        "rolling_24": lambda: RollingMeanForecaster(rolling_window),
    }
    result: Dict[str, List[Tuple[pd.Timestamp, float, Optional[float]]]] = {}
    for name, builder in builders.items():
        model = builder().fit(history)
        result[name] = model.forecast(test_df)
    return result


__all__ = [
    "NaiveForecaster",
    "SeasonalNaiveForecaster",
    "RollingMeanForecaster",
    "run_all_baselines",
]
