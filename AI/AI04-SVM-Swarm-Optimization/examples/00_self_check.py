"""Public interface checks for the student TODOs (not reference solutions)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from svmswarm.datasets import load_iris  # noqa: E402
from svmswarm.ga import GA, HybridGA  # noqa: E402
from svmswarm.naive_svm import NaiveSVM  # noqa: E402
from svmswarm.objective import (  # noqa: E402
    CONT_BOUNDS,
    CVObjective,
    decode,
    make_x,
    n_active,
    repair_mask,
    screening_prior,
)
from svmswarm.pso import HybridPSO, PSO  # noqa: E402


def _sphere(x: np.ndarray) -> float:
    return float(np.sum(np.square(x)))


def check_svm_kernel() -> None:
    X = np.array([[1.0, 0.0], [0.0, 2.0]], dtype=float)
    linear = NaiveSVM(kernel="linear")
    np.testing.assert_allclose(linear._gram(X), X @ X.T)

    rbf = NaiveSVM(kernel="rbf", gamma=0.5)
    rbf.gamma_value = 0.5
    K = rbf._gram(X)
    np.testing.assert_allclose(np.diag(K), 1.0)
    np.testing.assert_allclose(K, K.T)
    assert np.all((0.0 < K) & (K <= 1.0))


def check_svm() -> None:
    X, y, *_ = load_iris(classes=(0, 1))
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, stratify=y, random_state=42
    )
    scaler = StandardScaler().fit(X_train)
    model = NaiveSVM(kernel="linear", C=1.0, random_state=42)
    model.fit(scaler.transform(X_train), y_train)
    pred = model.predict(scaler.transform(X_test))
    assert pred.shape == y_test.shape
    assert set(np.unique(pred)) <= {-1.0, 1.0}
    assert float(np.mean(pred == y_test)) >= 0.9
    assert model.n_support > 0


def _check_result(result, budget: int, bounds: np.ndarray) -> None:
    assert result.n_evals == budget
    assert result.history.ndim == 2 and result.history.shape[1] == 2
    assert np.all(np.diff(result.history[:, 1]) <= 1e-12)
    assert np.all(result.best_x >= bounds[:, 0])
    assert np.all(result.best_x <= bounds[:, 1])


def check_ga() -> None:
    bounds = np.tile([-5.12, 5.12], (5, 1))
    result = GA(dim=5, bounds=bounds, n_pop=10, seed=0).optimize(_sphere, 300)
    _check_result(result, 300, bounds)
    assert result.best_value < 1.0


def check_hybrid_ga() -> None:
    def objective(x: np.ndarray) -> float:
        assert np.all(np.isin(x[2:], [0.0, 1.0]))
        assert np.sum(x[2:]) >= 1.0
        return float(np.sum(x[:2] ** 2) + 8.0 - np.sum(x[2:]))

    result = HybridGA(
        n_cont=2,
        n_bin=8,
        bounds=CONT_BOUNDS,
        n_pop=8,
        seed=2,
    ).optimize(objective, 64)
    assert result.n_evals == 64
    assert np.sum(result.best_x[2:]) >= 1.0


def check_pso() -> None:
    bounds = np.tile([-5.12, 5.12], (5, 1))
    result = PSO(n_particles=10, bounds=bounds, random_state=0).optimize(
        _sphere, 300
    )
    _check_result(result, 300, bounds)
    assert result.best_value < 1.0


def check_hybrid_pso() -> None:
    def objective(x: np.ndarray) -> float:
        assert np.all(np.isin(x[2:], [0.0, 1.0]))
        assert np.sum(x[2:]) >= 1.0
        return float(np.sum(x[:2] ** 2) + 8.0 - np.sum(x[2:]))

    result = HybridPSO(
        n_particles=8,
        n_cont=2,
        n_bin=8,
        bounds=CONT_BOUNDS,
        random_state=2,
    ).optimize(objective, 64)
    assert result.n_evals == 64
    assert np.sum(result.best_x[2:]) >= 1.0


def check_encoding() -> None:
    rng = np.random.default_rng(0)
    mask = np.array([1, 0, 1, 0], dtype=float)
    x = make_x(1.0, -2.0, mask)
    C, gamma, selected = decode(x)
    np.testing.assert_allclose([C, gamma], [10.0, 0.01])
    np.testing.assert_array_equal(selected, [0, 2])
    assert n_active(x) == 2

    empty = make_x(0.0, 0.0, np.zeros(4))
    repaired = repair_mask(empty, rng)
    assert n_active(repaired) == 1

    X, y = make_classification(
        n_samples=80,
        n_features=8,
        n_informative=3,
        n_redundant=0,
        random_state=0,
    )
    prior = screening_prior(X, y, top=3, p_top=0.8, p_rest=0.1)
    assert prior.shape == (8,)
    assert np.count_nonzero(np.isclose(prior, 0.8)) == 3
    assert np.count_nonzero(np.isclose(prior, 0.1)) == 5


def check_objective() -> None:
    X, y01 = make_classification(
        n_samples=90,
        n_features=8,
        n_informative=4,
        n_redundant=0,
        class_sep=1.5,
        random_state=1,
    )
    y = np.where(y01 == 1, 1.0, -1.0)
    objective = CVObjective(X, y, n_splits=3, penalty=0.01, cache=True)
    x = make_x(0.0, -1.0, np.ones(X.shape[1]))
    first = objective(x)
    fits_after_first = objective.n_fits
    second = objective(x)
    assert np.isfinite(first) and first == second
    assert objective.n_requests == 2
    assert fits_after_first == 3
    assert objective.n_fits == fits_after_first
    np.testing.assert_allclose(objective.loss(x), -first)


CHECKS = {
    "svm-kernel": check_svm_kernel,
    "svm": check_svm,
    "ga": check_ga,
    "hybrid-ga": check_hybrid_ga,
    "pso": check_pso,
    "hybrid-pso": check_hybrid_pso,
    "encoding": check_encoding,
    "objective": check_objective,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part", choices=[*CHECKS, "all"], default="all")
    args = parser.parse_args()
    selected = CHECKS.items() if args.part == "all" else [(args.part, CHECKS[args.part])]

    for name, check in selected:
        try:
            check()
        except (AssertionError, NotImplementedError, RuntimeError, TypeError, ValueError) as error:
            print(f"{name}: FAIL - {error}")
            return 1
        print(f"{name}: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
