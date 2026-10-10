"""Random-search baselines sharing the same candidate encoding and budget.

``RandomSearchHybrid`` draws candidates directly from the feasible set Omega
(u ~ U[-3,3], v ~ U[-4,1], each feature active with probability ``p_mask`` and
all-zero masks repaired).  ``RandomSearchContinuous`` only draws (u, v) and is
used for the keep-all-features ablation.  Both minimise ``objective.loss``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from .objective import CONT_BOUNDS, repair_mask
from .pso import OptResult


def _curves(hist: list) -> np.ndarray:
    return np.asarray(hist)


class RandomSearchHybrid:
    """Random search over the full space x = [u, v] + binary feature mask."""

    def __init__(self, n_feat: int = 500, p_mask: float = 0.2,
                 random_state: int = 0):
        self.n_feat = int(n_feat)
        self.p_mask = float(p_mask)
        self.rng = np.random.default_rng(random_state)

    def _sample(self) -> np.ndarray:
        u = self.rng.uniform(CONT_BOUNDS[0, 0], CONT_BOUNDS[0, 1])
        v = self.rng.uniform(CONT_BOUNDS[1, 0], CONT_BOUNDS[1, 1])
        mask = (self.rng.random(self.n_feat) < self.p_mask).astype(float)
        x = np.concatenate([[u, v], mask])
        return repair_mask(x, self.rng)

    def optimize(self, objective: Callable[[np.ndarray], float],
                 budget: int) -> OptResult:
        hist: list[list[float]] = []
        best_x = None
        best_val = np.inf
        evals = 0
        while evals < budget:
            x = self._sample()
            val = float(objective(x))
            evals += 1
            if val < best_val:
                best_val = val
                best_x = x
            hist.append([evals, best_val])
        return OptResult(best_x=best_x, best_value=best_val, n_evals=evals,
                         n_iter=evals, history=_curves(hist))


class RandomSearchContinuous:
    """Random search over [u, v] only (all features kept active)."""

    def __init__(self, random_state: int = 0):
        self.rng = np.random.default_rng(random_state)

    def optimize(self, objective: Callable[[np.ndarray], float],
                 budget: int) -> OptResult:
        hist: list[list[float]] = []
        best_x = None
        best_val = np.inf
        evals = 0
        while evals < budget:
            x = self.rng.uniform(CONT_BOUNDS[:, 0], CONT_BOUNDS[:, 1])
            val = float(objective(x))
            evals += 1
            if val < best_val:
                best_val = val
                best_x = x
            hist.append([evals, best_val])
        return OptResult(best_x=best_x, best_value=best_val, n_evals=evals,
                         n_iter=evals, history=_curves(hist))
