"""Particle swarm optimisation: continuous PSO and hybrid (continuous + binary) PSO.

Both optimisers *minimise* a black-box objective ``f(x) -> float``.  Validate them
on the Sphere function before attaching an SVM objective.

Project encoding convention (see ``objective.py``)::

    x = [u, v, m_0, m_1, ..., m_{d-1}]
        u = log10(C)      (continuous)
        v = log10(gamma)  (continuous)
        m_j in {0, 1}     (feature mask, binary)

``HybridPSO`` uses the standard velocity update on every dimension, but the
binary dimensions switch to the Binary-PSO position rule (Kennedy & Eberhart,
1997): velocity -> sigmoid -> Bernoulli sample.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np


@dataclass
class OptResult:
    """Result of one optimisation run.

    history is an (n, 2) array: column 0 = objective evaluations spent so far,
    column 1 = best (minimum) objective value found so far.
    """
    best_x: np.ndarray
    best_value: float
    n_evals: int
    n_iter: int
    history: np.ndarray = field(default_factory=lambda: np.zeros((0, 2)))


class _BasePSO:
    """Shared bookkeeping: population init, budgeted initial evaluation."""

    def _init_positions(self) -> np.ndarray:
        raise NotImplementedError

    def _init_velocities(self, n: int, dim: int) -> np.ndarray:
        raise NotImplementedError

    def _move(self, vel: np.ndarray, pos: np.ndarray, lo: np.ndarray, hi: np.ndarray):
        """In-place update of velocities/positions; returns nothing."""
        raise NotImplementedError

    def _repair_positions(self, pos: np.ndarray) -> None:
        pass

    def optimize(self, objective: Callable[[np.ndarray], float],
                 budget: int) -> OptResult:
        # TODO 8（学生实现）：实现受评价预算约束的 PSO 主循环。
        # 初始化位置、速度、pbest 和 gbest；每轮按惯性项、认知项和社会项
        # 更新速度，再调用子类 _move 与 _repair_positions。支持可选的 w_end
        # 线性衰减；总 objective 调用数不得超过 budget。history 每行记录
        # [累计评价次数, 历史最优损失]，第二列应单调不增。
        raise NotImplementedError("TODO 8: implement the budgeted PSO loop")


class PSO(_BasePSO):
    """Continuous PSO with inertia weight, personal/global best and clamping.

    Parameters
    ----------
    n_particles : int
    bounds : array-like of shape (dim, 2)
        Lower / upper bound of every continuous dimension.
    w, c1, c2 : float
        Inertia, cognitive and social coefficients.
    w_end : float or None
        If given, the inertia weight decreases linearly from ``w`` to ``w_end``
        over the expected number of iterations (Shi & Eberhart 1998 style).
    v_max_frac : float
        Velocity limit as a fraction of each dimension's width.
    max_iter, random_state
    """

    def __init__(self, n_particles: int = 10, bounds=None, w: float = 0.7,
                 c1: float = 1.5, c2: float = 1.5, w_end: float | None = None,
                 v_max_frac: float = 0.3,
                 max_iter: int = 500, random_state: int = 0):
        bounds = np.asarray(bounds, dtype=float)
        if bounds.ndim != 2 or bounds.shape[1] != 2:
            raise ValueError("bounds must have shape (dim, 2)")
        self.bounds = bounds
        self.dim = bounds.shape[0]
        self.lo = bounds[:, 0]
        self.hi = bounds[:, 1]
        self.width = self.hi - self.lo
        self.n_particles = int(n_particles)
        self.w, self.c1, self.c2 = float(w), float(c1), float(c2)
        self.w_end = float(w_end) if w_end is not None else None
        self.v_lim = self.width * float(v_max_frac)
        self.max_iter = int(max_iter)
        self.rng = np.random.default_rng(random_state)

    def _init_positions(self) -> np.ndarray:
        # TODO 9a（学生实现）：在连续边界内均匀初始化粒子位置。
        raise NotImplementedError("TODO 9a: initialise continuous positions")

    def _init_velocities(self, n: int, dim: int) -> np.ndarray:
        # TODO 9b（学生实现）：在逐维速度限制内均匀初始化速度。
        raise NotImplementedError("TODO 9b: initialise continuous velocities")

    def _move(self, vel: np.ndarray, pos: np.ndarray, lo: np.ndarray, hi: np.ndarray):
        # TODO 9c（学生实现）：限制速度、更新位置并裁剪边界。
        # 粒子撞到边界时，将对应维度速度置零；所有更新均原地完成。
        raise NotImplementedError("TODO 9c: move continuous particles")


class HybridPSO(_BasePSO):
    """PSO over mixed variables: ``n_cont`` continuous dims + ``n_bin`` binary dims.

    ``bounds`` describes only the continuous dimensions (shape (n_cont, 2)).
    Binary velocities are clamped to ``[-v_bin_max, v_bin_max]`` and converted to
    bit probabilities through the logistic sigmoid.  All-zero masks are repaired
    by activating one random feature (keeps solutions in Omega, README eq. 4).
    """

    def __init__(self, n_particles: int = 10, n_cont: int = 2, n_bin: int = 500,
                 bounds=None, w: float = 0.7, c1: float = 1.5, c2: float = 1.5,
                 w_end: float | None = None,
                 v_max_frac: float = 0.3, v_bin_max: float = 4.0,
                 p_init: float = 0.5, max_iter: int = 500, random_state: int = 0,
                 mask_prior: np.ndarray | None = None):
        if bounds is None:
            bounds = [[-3.0, 3.0], [-4.0, 1.0]]
        bounds = np.asarray(bounds, dtype=float)
        self.n_cont = int(n_cont)
        self.n_bin = int(n_bin)
        self.dim = self.n_cont + self.n_bin
        self.lo = bounds[:, 0]
        self.hi = bounds[:, 1]
        self.width = self.hi - self.lo
        self.n_particles = int(n_particles)
        self.w, self.c1, self.c2 = float(w), float(c1), float(c2)
        self.w_end = float(w_end) if w_end is not None else None
        self.v_lim = self.width * float(v_max_frac)
        self.v_bin_max = float(v_bin_max)
        self.p_init = float(p_init)
        self.max_iter = int(max_iter)
        self.rng = np.random.default_rng(random_state)
        if mask_prior is not None:
            mask_prior = np.asarray(mask_prior, dtype=float)
            if mask_prior.shape != (self.n_bin,):
                raise ValueError("mask_prior must have shape (n_bin,)")
        self.mask_prior = mask_prior

    def _repair_masks(self, pos: np.ndarray) -> None:
        # TODO 10a（学生实现）：逐行修复全零特征掩码。
        raise NotImplementedError("TODO 10a: repair empty particle masks")

    def _repair_positions(self, pos: np.ndarray) -> None:
        self._repair_masks(pos)

    def _init_positions(self) -> np.ndarray:
        # TODO 10b（学生实现）：初始化连续位置与二进制特征掩码。
        # 掩码使用 mask_prior；未提供时使用统一的 p_init，并修复空掩码。
        raise NotImplementedError("TODO 10b: initialise hybrid positions")

    def _init_velocities(self, n: int, dim: int) -> np.ndarray:
        # TODO 10c（学生实现）：连续段随机初始化，二进制段速度初始化为 0。
        raise NotImplementedError("TODO 10c: initialise hybrid velocities")

    def _move(self, vel: np.ndarray, pos: np.ndarray, lo: np.ndarray, hi: np.ndarray):
        # TODO 10d（学生实现）：连续段按标准 PSO 移动并处理边界；二进制段
        # 将速度限制到 [-v_bin_max, v_bin_max]，经 sigmoid 转为激活概率，
        # 再进行 Bernoulli 采样。所有更新均原地完成。
        raise NotImplementedError("TODO 10d: move hybrid particles")
