"""Genetic algorithms: real-coded GA and hybrid-chromosome GA (feature mask + (u, v)).

Both minimise a black-box objective ``f(x) -> float``.  Chromosomes of the hybrid
GA are ``x = [u, v, m_0, ..., m_{d-1}]``: the continuous part uses arithmetic
crossover and Gaussian mutation, the binary part uses uniform crossover and
bit-flip mutation.  Selection is tournament-based and the best ``elite_count``
individuals survive unchanged (their fitness is reused, never re-evaluated).

Operator defaults follow the teaching documentation in README section 7:
tournament size 3, arithmetic crossover rate ~0.9, per-gene Gaussian mutation,
1 elite.  All positions are clipped into their bounds and all-zero feature masks
are repaired by activating one random feature.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from .pso import OptResult


@dataclass
class _GAConfig:
    n_pop: int = 10
    tournament: int = 3
    pc: float = 0.9
    pm_cont: float = 0.2
    mut_scale: float = 0.05
    pm_bin: float = 0.002
    elite: int = 1
    max_gen: int = 500
    seed: int = 0


class _BaseGA:
    def __init__(self, n_pop: int = 10, tournament: int = 3, pc: float = 0.9,
                 pm_cont: float = 0.2, mut_scale: float = 0.05,
                 pm_bin: float = 0.002, elite: int = 1, max_gen: int = 500,
                 seed: int = 0):
        self.cfg = _GAConfig(n_pop=n_pop, tournament=tournament, pc=pc,
                             pm_cont=pm_cont, mut_scale=mut_scale, pm_bin=pm_bin,
                             elite=elite, max_gen=max_gen, seed=seed)
        self.rng = np.random.default_rng(seed)

    # subclass hooks -------------------------------------------------------
    @property
    def dim(self) -> int:  # pragma: no cover - abstract
        raise NotImplementedError

    def _init_individual(self) -> np.ndarray:
        raise NotImplementedError

    def _mutate(self, ind: np.ndarray) -> None:
        raise NotImplementedError

    def _recombine(self, p1: np.ndarray, p2: np.ndarray
                   ) -> tuple[np.ndarray, np.ndarray]:
        raise NotImplementedError

    def _bounds_check(self, ind: np.ndarray) -> None:
        raise NotImplementedError

    def _repair(self, ind: np.ndarray) -> None:
        """Keep the individual feasible (e.g. non-empty feature mask)."""

    def _tournament(self, pop: list, fits: np.ndarray) -> np.ndarray:
        # TODO 4（学生实现）：锦标赛选择。
        # 随机抽取 tournament 个索引，返回其中适应度最小者的副本；不得
        # 返回原数组引用，否则后续变异会破坏父代。
        raise NotImplementedError("TODO 4: implement tournament selection")

    def optimize(self, objective: Callable[[np.ndarray], float],
                 budget: int) -> OptResult:
        # TODO 5（学生实现）：实现受评价预算约束的 GA 主循环。
        # 需要完成种群初始化与评价、精英保留、锦标赛选择、交叉、变异、
        # 边界处理、可行性修复和全局最优更新。elite 的既有适应度必须
        # 复用，不得重复调用 objective；总调用次数不得超过 budget。
        # history 每行记录 [累计评价次数, 历史最优损失]，第二列应单调不增。
        raise NotImplementedError("TODO 5: implement the budgeted GA loop")


class GA(_BaseGA):
    """Real-coded GA over a continuous box (used for test functions and for the
    C/gamma-only ablation where all features are always active)."""

    def __init__(self, dim: int = 2, bounds=None, n_pop: int = 10,
                 tournament: int = 3, pc: float = 0.9, pm_cont: float = 0.2,
                 mut_scale: float = 0.05, elite: int = 1, max_gen: int = 500,
                 seed: int = 0):
        super().__init__(n_pop=n_pop, tournament=tournament, pc=pc, pm_cont=pm_cont,
                         mut_scale=mut_scale, elite=elite, max_gen=max_gen, seed=seed)
        if bounds is None:
            bounds = [[-3.0, 3.0], [-4.0, 1.0]]
        bounds = np.asarray(bounds, dtype=float)
        if bounds.ndim != 2 or bounds.shape[1] != 2:
            raise ValueError("bounds must have shape (dim, 2)")
        if bounds.shape[0] != dim:
            raise ValueError("dim and bounds rows disagree")
        self._dim = int(dim)
        self.bounds = bounds
        self.lo = bounds[:, 0]
        self.hi = bounds[:, 1]
        self.sigma = self.cfg.mut_scale * (self.hi - self.lo)

    @property
    def dim(self) -> int:
        return self._dim

    def _init_individual(self) -> np.ndarray:
        # TODO 6a（学生实现）：在连续边界内均匀初始化一个个体。
        raise NotImplementedError("TODO 6a: initialise a real-coded individual")

    def _recombine(self, p1: np.ndarray, p2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        # TODO 6b（学生实现）：用同一随机系数进行算术交叉并返回两个子代。
        raise NotImplementedError("TODO 6b: implement arithmetic crossover")

    def _mutate(self, ind: np.ndarray) -> None:
        # TODO 6c（学生实现）：按 pm_cont 独立选择基因并施加高斯变异。
        raise NotImplementedError("TODO 6c: implement Gaussian mutation")

    def _bounds_check(self, ind: np.ndarray) -> None:
        # TODO 6d（学生实现）：原地裁剪到连续搜索边界。
        raise NotImplementedError("TODO 6d: enforce continuous bounds")


class HybridGA(_BaseGA):
    """GA over x = [u, v] + binary feature mask."""

    def __init__(self, n_cont: int = 2, n_bin: int = 500, bounds=None,
                 n_pop: int = 10, tournament: int = 3, pc: float = 0.9,
                 pm_cont: float = 0.2, mut_scale: float = 0.05,
                 pm_bin: float = 0.002, elite: int = 1, max_gen: int = 500,
                 seed: int = 0, mask_prior: np.ndarray | None = None):
        super().__init__(n_pop=n_pop, tournament=tournament, pc=pc, pm_cont=pm_cont,
                         mut_scale=mut_scale, pm_bin=pm_bin, elite=elite,
                         max_gen=max_gen, seed=seed)
        if bounds is None:
            bounds = [[-3.0, 3.0], [-4.0, 1.0]]
        bounds = np.asarray(bounds, dtype=float)
        self.n_cont = int(n_cont)
        self.n_bin = int(n_bin)
        self.lo = bounds[:, 0]
        self.hi = bounds[:, 1]
        self.sigma = self.cfg.mut_scale * (self.hi - self.lo)
        self._dim = self.n_cont + self.n_bin
        if mask_prior is not None:
            mask_prior = np.asarray(mask_prior, dtype=float)
            if mask_prior.shape != (self.n_bin,):
                raise ValueError("mask_prior must have shape (n_bin,)")
        self.mask_prior = mask_prior

    @property
    def dim(self) -> int:
        return self._dim

    def _init_individual(self) -> np.ndarray:
        # TODO 7a（学生实现）：初始化 [u, v, mask...] 混合染色体。
        # 连续段均匀采样；二进制段使用 mask_prior，未提供时概率为 0.5；
        # 最后调用 _repair 保证至少选择一个特征。
        raise NotImplementedError("TODO 7a: initialise a hybrid chromosome")

    def _recombine(self, p1: np.ndarray, p2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        # TODO 7b（学生实现）：连续段使用算术交叉，掩码段使用均匀交叉；
        # 第二个子代采用互补的父代来源。
        raise NotImplementedError("TODO 7b: implement hybrid crossover")

    def _mutate(self, ind: np.ndarray) -> None:
        # TODO 7c（学生实现）：连续段高斯变异，掩码段按 pm_bin 位翻转。
        raise NotImplementedError("TODO 7c: implement hybrid mutation")

    def _bounds_check(self, ind: np.ndarray) -> None:
        # TODO 7d（学生实现）：仅裁剪连续段，二进制段保持 0/1。
        raise NotImplementedError("TODO 7d: enforce hybrid bounds")

    def _repair(self, ind: np.ndarray) -> None:
        # TODO 7e（学生实现）：全零掩码时随机激活一个特征。
        raise NotImplementedError("TODO 7e: repair an empty feature mask")
