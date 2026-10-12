"""Teaching SVM trained with a simplified Sequential Minimal Optimization (SMO).

Implements the soft-margin SVM dual problem for binary labels in {-1, +1} with a
linear or RBF kernel.  The simplified SMO (Platt, 1998; textbook variant of
"Machine Learning in Action") optimises the dual objective by repeatedly
updating *two* Lagrange multipliers at a time while keeping the equality
constraint satisfied.

This module is deliberately small and readable.  It is used to *understand* the
max-margin / kernel / dual / SMO ideas on the small Iris subtask and is compared
against :class:`sklearn.svm.SVC`; it does not carry the MADELON workload (the
README states the high-dimensional pipeline relies on the mature sklearn SVC).
"""
from __future__ import annotations

import numpy as np


class NaiveSVM:
    """Binary SVM (labels in {-1, +1}) trained by simplified SMO.

    Parameters
    ----------
    C : float
        Soft-margin penalty coefficient.
    kernel : {"linear", "rbf"}
        Kernel type.
    gamma : float or "scale"
        RBF kernel width.  "scale" -> 1 / (n_features * X.var()).
    tol : float
        KKT tolerance used to decide whether an alpha is worth updating.
    max_passes : int
        Maximum number of passes with no alpha change before early stopping.
    random_state : int or None
        Seed for the (random) choice of the second multiplier.
    """

    def __init__(self, C: float = 1.0, kernel: str = "rbf", gamma: float | str = "scale",
                 tol: float = 1e-3, max_passes: int = 20, random_state: int | None = 42):
        if kernel not in ("linear", "rbf"):
            raise ValueError(f"kernel must be 'linear' or 'rbf', got {kernel!r}")
        if C <= 0:
            raise ValueError("C must be positive")
        self.C = float(C)
        self.kernel = kernel
        self.gamma = gamma
        self.tol = float(tol)
        self.max_passes = int(max_passes)
        self.random_state = random_state
        self._rng = np.random.default_rng(random_state)

        # Fitted state
        self.X_sv: np.ndarray | None = None
        self.y_sv: np.ndarray | None = None
        self.alpha_sv: np.ndarray | None = None
        self.b: float = 0.0
        self.sv_index: np.ndarray | None = None
        self.n_iter_passes: int = 0
        self.gamma_value: float | None = None

    # ------------------------------------------------------------------ fit
    def _gram(self, X: np.ndarray) -> np.ndarray:
        """Compute the (m x m) kernel matrix of the training set."""
        # TODO 1（学生实现）：计算训练样本的 Gram 矩阵。
        # linear 核返回 X @ X.T；RBF 核应以向量化方式计算两两平方距离，
        # 将浮点误差导致的负距离截为 0，再计算 exp(-gamma * distance^2)。
        raise NotImplementedError("TODO 1: implement linear and RBF Gram matrices")

    def _decision_row(self, i: int, K: np.ndarray) -> float:
        """f(x_i) = sum_j alpha_j y_j K(x_j, x_i) + b  (without label i's own term)."""
        return float(np.dot(self.alphas * self.y, K[:, i]) + self.b)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "NaiveSVM":
        """Train on (X, y); y must take values in {-1, +1}."""
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float).ravel()
        if set(np.unique(y)) - {-1.0, 1.0}:
            raise ValueError("y must contain only -1 and +1")
        m, d = X.shape

        if self.kernel == "rbf":
            if self.gamma == "scale":
                var = X.var()
                self.gamma_value = 1.0 / (d * var) if var > 0 else 1.0
            else:
                self.gamma_value = float(self.gamma)

        # TODO 2（学生实现）：使用简化 SMO 训练二分类 SVM。
        # 需要完成：初始化 alpha/b；逐样本检查 KKT 违反；随机选择第二个
        # 乘子；计算 L/H 与 eta；更新两个 alpha；计算 b1/b2 并更新偏置；
        # 按“连续无更新轮数”停止。训练结束后只保存 alpha > 1e-5 的支持
        # 向量到 X_sv/y_sv/alpha_sv，并记录 sv_index 和 n_iter_passes。
        # 返回 self，且不得调用 sklearn.svm.SVC 代替本实现。
        raise NotImplementedError("TODO 2: implement simplified SMO training")

    # ------------------------------------------------------------- predict
    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """Signed distance to the separating hyperplane, f(x) = sum alpha y K + b."""
        X = np.asarray(X, dtype=float)
        if self.X_sv is None:
            raise RuntimeError("fit() must be called before decision_function()")
        # TODO 3（学生实现）：根据保存的支持向量计算决策函数。
        # linear 核可先恢复权重向量 w；RBF 核计算待预测样本与所有支持
        # 向量的核值。返回 shape=(n_samples,) 的浮点数组。
        raise NotImplementedError("TODO 3: implement SVM decision function")

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.where(self.decision_function(X) >= 0.0, 1.0, -1.0)

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        return float(np.mean(self.predict(X) == np.asarray(y).ravel()))

    @property
    def n_support(self) -> int:
        return 0 if self.alpha_sv is None else int(len(self.alpha_sv))

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return (f"NaiveSVM(C={self.C:g}, kernel={self.kernel!r}, "
                f"gamma={self.gamma!r}, SVs={self.n_support})")
