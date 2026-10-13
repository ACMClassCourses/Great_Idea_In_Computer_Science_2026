"""数据接入与时间切分（Basic TODO 1–2，从零实现，不调库）。

TODO 1：合并 ``dteday`` + ``hr`` 为时间戳，排序、查重、找缺失小时，
        输出 ``(timestamp, value)`` 序列。
TODO 2：按时间**固定**前 60% 训练、中 20% 开发、后 20% 测试，记录具体日期范围；
        **禁止随机打乱**。

设计边界（对应 README A 节）：
- 目标值默认取 ``cnt``（= casual + registered）。``casual`` / ``registered`` 在目标小时
  才等于 cnt 的拆分，因此**不能作为提前可得的输入**，这里只用于完整性校验。
- 切分按时间顺序切片，而不是按行随机。这样测试集永远在时间之后，模拟"向前预测"。
- 缺失小时检测基于"理想连续小时网格"；只要某连续小时在数据中不存在就报缺失。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd


def load_series(
    path: str,
    value_col: str = "cnt",
    dteday_col: str = "dteday",
    hr_col: str = "hr",
    casual_col: str = "casual",
    registered_col: str = "registered",
) -> pd.DataFrame:
    """TODO 1（上半）：读入 CSV 并合并时间戳。

    返回按时间升序排序、带 ``timestamp`` 列的 DataFrame。
    同时做：查重（同一 timestamp 出现多次报警）、可选字段完整性校验。

    实现提示：
    - ``pd.to_datetime(dteday) + pd.to_timedelta(int(hr), unit="h")`` 得到时间戳。
    - ``hr`` 必须在 0–23；``timestamp`` 必须唯一，否则报错。
    - 若 ``casual`` / ``registered`` 列存在，校验 ``casual + registered == cnt``。
    """
    raise NotImplementedError(
        "TODO 1（上半）：读 CSV，合并 dteday+hr 为 timestamp，排序、查重、完整性校验，"
        "返回 [timestamp, value] 的 DataFrame。"
    )


def find_missing_hours(ts: pd.Series, value: pd.Series) -> List[pd.Timestamp]:
    """TODO 1（下半）：在理想连续小时网格上找出缺失的小时。

    理想网格 = 从最小到最大时间戳、步长 1 小时。返回缺失时间点的列表。
    """
    raise NotImplementedError(
        "TODO 1（下半）：用 pd.date_range(min, max, freq='h') 构造理想网格，"
        "返回不在 ts 中的时间点列表。"
    )


@dataclass
class TimeSplit:
    """TODO 2：时间切分结果，记录各段的具体日期范围（禁随机）。"""

    train: pd.DataFrame
    dev: pd.DataFrame
    test: pd.DataFrame
    train_range: Tuple[pd.Timestamp, pd.Timestamp]
    dev_range: Tuple[pd.Timestamp, pd.Timestamp]
    test_range: Tuple[pd.Timestamp, pd.Timestamp]
    n_missing: int

    def summary(self) -> str:
        fmt = "%Y-%m-%d %H:%M"
        return (
            f"train {self.train_range[0].strftime(fmt)} ~ {self.train_range[1].strftime(fmt)}"
            f"  (n={len(self.train)})\n"
            f"dev   {self.dev_range[0].strftime(fmt)} ~ {self.dev_range[1].strftime(fmt)}"
            f"  (n={len(self.dev)})\n"
            f"test  {self.test_range[0].strftime(fmt)} ~ {self.test_range[1].strftime(fmt)}"
            f"  (n={len(self.test)})\n"
            f"missing hours in grid: {self.n_missing}"
        )


def time_split(
    df: pd.DataFrame,
    train_frac: float = 0.6,
    dev_frac: float = 0.2,
) -> TimeSplit:
    """TODO 2：按时间顺序固定切分（不随机）。

    ``train_frac`` 与 ``dev_frac`` 作用于"小时数"（行数），而非随机样本。
    剩余部分归测试集。记录各段的具体日期范围，并统计网格内缺失小时数。
    """
    raise NotImplementedError(
        "TODO 2：按时间顺序切片（df.iloc[:n_train] 等），返回 TimeSplit，"
        "记录 train/dev/test 的日期范围与 n_missing。禁止随机打乱。"
    )


def load_and_split(
    path: str,
    value_col: str = "cnt",
    train_frac: float = 0.6,
    dev_frac: float = 0.2,
) -> TimeSplit:
    """串联 TODO 1 与 TODO 2：读入 -> 校验 -> 时间切分。"""
    df = load_series(path, value_col=value_col)
    return time_split(df, train_frac=train_frac, dev_frac=dev_frac)


__all__ = [
    "load_series",
    "find_missing_hours",
    "time_split",
    "load_and_split",
    "TimeSplit",
]
