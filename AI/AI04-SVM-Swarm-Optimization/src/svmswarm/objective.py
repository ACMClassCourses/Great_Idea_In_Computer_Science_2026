"""Leak-free stratified-K-fold SVM objective with a feature-mask penalty.

Candidate encoding (shared by GA, hybrid PSO and random search)::

    x = [u, v, m_0, ..., m_{d-1}]
        u = log10(C)      in [-3, 3]
        v = log10(gamma)  in [-4, 1]
        m_j in {0, 1}     feature j selected?

Objective (README section 4)::

    J(theta) = S_CV(theta) - lambda * ||m||_0 / d      (maximised)

with C = 10^u, gamma = 10^v and S_CV the mean stratified K-fold validation
accuracy of ``Pipeline(StandardScaler, SVC(kernel='rbf'))`` on the columns
selected by m.  The scaler is fitted per fold inside the pipeline, so no
validation-fold statistics leak into training.  A fixed set of fold indices is
created once per data set and reused for every candidate and every method.

Feature masking is a hyper-parameter chosen by the optimiser (never learned from
data), hence applying the mask before CV is leak-free.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np
from sklearn.feature_selection import f_classif
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

CONT_BOUNDS = np.asarray([[-3.0, 3.0], [-4.0, 1.0]])   # u = log10(C), v = log10(gamma)


def make_x(u: float, v: float, mask: np.ndarray) -> np.ndarray:
    """Assemble the full candidate vector from (u, v, boolean mask)."""
    # TODO 11a（学生实现）：按 [u, v, m_0, ..., m_(d-1)] 编码候选。
    raise NotImplementedError("TODO 11a: encode a mixed candidate")


def decode(x: np.ndarray, n_feat: int | None = None) -> tuple[float, float, np.ndarray]:
    """Return (C, gamma, selected-index array) from a full candidate vector."""
    # TODO 11b（学生实现）：解码 C=10^u、gamma=10^v，并返回掩码中
    # 大于 0.5 的特征索引；n_feat 非空时只读取指定长度的掩码。
    raise NotImplementedError("TODO 11b: decode a mixed candidate")


def n_active(x: np.ndarray) -> int:
    # TODO 11c（学生实现）：统计被选择的特征数。
    raise NotImplementedError("TODO 11c: count active features")


def repair_mask(x: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Return x with a guaranteed non-empty feature mask (constraint ||m||_0 >= 1)."""
    # TODO 11d（学生实现）：掩码全零时复制 x 并随机激活一个特征；
    # 已有特征被选择时可直接返回原对象。
    raise NotImplementedError("TODO 11d: repair an empty candidate mask")


def screening_prior(X: np.ndarray, y: np.ndarray, top: int = 40,
                    p_top: float = 0.75, p_rest: float = 0.01) -> np.ndarray:
    """Per-feature activation probabilities used to warm-start GA / PSO masks.

    An ANOVA F-score ranks the features once on the *training* set (the sealed
    validation set never enters) and the returned vector gives the top-ranked
    features a high activation probability while the rest stay explorable with a
    low probability.  This is a documented search-initialisation heuristic; the
    final comparison itself always uses the fixed stratified CV folds.
    """
    # TODO 11e（学生实现）：使用 f_classif 对训练集特征排序，构造逐特征
    # 激活概率。top 个特征取 p_top，其余取 p_rest；不得读取 Validation。
    raise NotImplementedError("TODO 11e: build the screening prior")


class CVObjective:
    """Stratified K-fold CV accuracy - feature-count penalty for one data set.

    Parameters
    ----------
    X, y : training data (y in {-1, +1}).
    n_splits : number of CV folds.
    cv_seed : random state used to create the (fixed) fold split.
    penalty : lambda in J = S_CV - lambda * ||m||_0 / d.
    cv_jobs : folds evaluated in parallel with joblib (results are identical,
        only wall-clock time changes).
    cache : remember (u, v, mask) -> J to avoid repeated model fitting.
    """

    def __init__(self, X: np.ndarray, y: np.ndarray, n_splits: int = 5,
                 cv_seed: int = 42, penalty: float = 0.01, cv_jobs: int = 1,
                 cache: bool = True):
        self.X = np.asarray(X, dtype=float)
        self.y = np.asarray(y, dtype=float).ravel()
        self.n_feat = self.X.shape[1]
        self.penalty = float(penalty)
        self.cv_jobs = int(cv_jobs)
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=cv_seed)
        self.folds: list[tuple[np.ndarray, np.ndarray]] = list(
            cv.split(self.X, self.y))
        self._cache: dict[tuple, float] = {}
        self.use_cache = bool(cache)
        self.n_requests = 0        # number of objective evaluations requested
        self.n_fits = 0            # number of SVC fits actually performed

    # ---------------------------------------------------------------- decode
    def _key(self, u: float, v: float, sel: np.ndarray) -> tuple:
        return (round(u, 12), round(v, 12), tuple(int(s) for s in sel))

    def _cv_score(self, C: float, gamma: float, sel: np.ndarray) -> float:
        """Mean fold accuracy on the columns ``sel`` (scaler fitted per fold)."""
        # TODO 12a（学生实现）：选择 sel 对应列，构造
        # Pipeline(StandardScaler, RBF-SVC)，并使用 self.folds 交叉验证。
        # 标准化必须位于 Pipeline 内；完成后增加实际拟合次数 n_fits。
        raise NotImplementedError("TODO 12a: implement leak-free CV scoring")

    def _J(self, u: float, v: float, sel: np.ndarray) -> float:
        # TODO 12b（学生实现）：查询缓存；未命中时计算 CV 准确率与特征
        # 数量惩罚 J=S_CV-lambda*|m|/d，并按配置写回缓存。
        raise NotImplementedError("TODO 12b: implement the cached objective J")

    # ------------------------------------------------------------ public API
    def __call__(self, x: np.ndarray) -> float:
        """Objective value J(x) (higher is better)."""
        self.n_requests += 1
        u, v, sel = x[0], x[1], self._sel_from_x(x)
        return self._J(u, v, sel)

    def loss(self, x: np.ndarray) -> float:
        """Minimisation view used by GA / PSO / random search: loss = -J."""
        return -self.__call__(x)

    def raw_cv_accuracy(self, x: np.ndarray) -> float:
        """Mean CV accuracy of candidate x without the mask penalty.

        Uses the cache when available (no extra fitting); otherwise performs one
        additional CV evaluation.
        """
        x = np.asarray(x, dtype=float)
        u, v, sel = float(x[0]), float(x[1]), self._sel_from_x(x)
        key = self._key(u, v, sel)
        if self.use_cache and key in self._cache:
            return float(self._cache[key]) + self.penalty * (sel.size / self.n_feat)
        return self._cv_score(10.0 ** u, 10.0 ** v, sel)

    @staticmethod
    def _sel_from_x(x: np.ndarray) -> np.ndarray:
        return np.flatnonzero(x[2:] > 0.5)


def make_cv_only_objective(obj: CVObjective, n_feat: int | None = None):
    """Objective for the ablation that keeps ALL features and tunes (C, gamma).

    Returns ``f(x2) -> float`` minimisation loss for a 2-D vector [u, v].
    """
    if n_feat is None:
        n_feat = obj.n_feat
    all_sel = np.arange(n_feat)

    def f(x2: np.ndarray) -> float:
        obj.n_requests += 1
        x2 = np.asarray(x2, dtype=float)
        key = obj._key(float(x2[0]), float(x2[1]), all_sel)
        if obj.use_cache and key in obj._cache:
            j = obj._cache[key]
        else:
            score = obj._cv_score(10.0 ** float(x2[0]), 10.0 ** float(x2[1]), all_sel)
            j = score - obj.penalty * 1.0     # ||m||_0 = d -> penalty term = lambda
            if obj.use_cache:
                obj._cache[key] = j
        return -j

    return f
