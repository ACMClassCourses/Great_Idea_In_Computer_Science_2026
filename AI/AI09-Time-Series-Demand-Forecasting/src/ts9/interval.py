"""滚动残差区间（Advance 可选增强，Basic 不需要改动）。

围绕点预测构造对称区间 ``[pred - q, pred + q]``，半径 q 由**过去（样本外）残差**
的绝对值得分位数估计。对应 G4。

区间半径规则（README A 节第 3 点）：若窗口有 m 个残差，用排序后第
``ceil((m+1)*(1-alpha))`` 个作为参考半径；若序号超出 m，则扩大窗口或明确使用
"无穷半径"（本项目用历史最大残差兜底，并在报告中说明）。

注意：需求序列含季节、漂移与相关，简单滚动残差区间**不能**自动宣称有
split-conformal 的理论覆盖保证；本项目只报告实测覆盖（见 evaluate.py）。
"""

from __future__ import annotations

import math
from typing import List, Optional

import numpy as np


def radius_from_residuals(residuals: List[float], alpha: float) -> float:
    """给定历史绝对残差列表与目标显著性 alpha，返回区间半径 q。

    alpha=0.1 对应 90% 名义覆盖；alpha=0.2 对应 80%。
    序号 = ceil((m+1)*(1-alpha))，越界时退回最大残差（"无穷半径"兜底）。
    """
    if not residuals:
        return float("inf")
    abs_r = np.sort(np.abs(np.asarray(residuals, dtype=float)))
    m = len(abs_r)
    k = math.ceil((m + 1) * (1.0 - alpha))
    if k < 1:
        k = 1
    if k > m:
        # 窗口样本不足：退回历史最大残差，并应在报告中标注
        return float(abs_r[-1])
    return float(abs_r[k - 1])


class RollingResidualInterval:
    """维护一个滚动残差窗口，按需给出半径并更新窗口。"""

    def __init__(self, window: int = 168, alphas: Optional[List[float]] = None):
        self.window = int(window)
        self.alphas = alphas or [0.2, 0.1]
        self._buf: List[float] = []

    def radius(self, alpha: float) -> float:
        return radius_from_residuals(self._buf, alpha)

    def update(self, residual: float) -> None:
        """真值到达后，把本次残差加入窗口（保持长度上限）。"""
        self._buf.append(float(residual))
        if len(self._buf) > self.window:
            self._buf.pop(0)

    def warmup(self, residuals: List[float]) -> None:
        """用开发期末尾的样本外残差初始化窗口（暖启动）。"""
        self._buf = list(residuals)[-self.window :]


__all__ = ["radius_from_residuals", "RollingResidualInterval"]
