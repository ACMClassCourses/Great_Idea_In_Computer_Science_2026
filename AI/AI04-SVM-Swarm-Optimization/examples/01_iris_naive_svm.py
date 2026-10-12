"""Example 1 – Naive (SMO) SVM vs sklearn.svm.SVC on an Iris binary subtask.

Runs the two-class subtask versicolor vs virginica (default) with a linear and
an RBF kernel and reports test accuracy, support-vector counts and run times.
The naive implementation only needs numpy.

Run:  python examples/01_iris_naive_svm.py
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
from sklearn.model_selection import train_test_split  # noqa: E402
from sklearn.svm import SVC  # noqa: E402

from svmswarm.datasets import load_iris  # noqa: E402
from svmswarm.naive_svm import NaiveSVM  # noqa: E402

PAIR_NAMES = {0: "setosa", 1: "versicolor", 2: "virginica"}


def compare(pair=(1, 2), kernel="rbf", seed=42):
    X, y, _, class_names, _ = load_iris(classes=pair)
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.3, stratify=y, random_state=seed)

    print(f"\nIris subtask: {class_names[0]} (-1) vs {class_names[1]} (+1), "
          f"n={len(y)} ({X_tr.shape[0]} train / {X_te.shape[0]} test), kernel={kernel}")

    t0 = time.perf_counter()
    naive = NaiveSVM(C=1.0, kernel=kernel, gamma="scale", random_state=seed).fit(X_tr, y_tr)
    t_naive = time.perf_counter() - t0

    t0 = time.perf_counter()
    sk = SVC(C=1.0, kernel=kernel, gamma="scale").fit(X_tr, y_tr)
    t_sk = time.perf_counter() - t0

    acc_naive = naive.score(X_te, y_te)
    acc_sk = sk.score(X_te, y_te)

    # chance level: majority class of the training split
    chance = max(np.mean(y_tr == 1), np.mean(y_tr == -1))
    print(f"  chance level                 : {chance:.3f}")
    print(f"  NaiveSVM  train acc {naive.score(X_tr, y_tr):.4f} "
          f"| test acc {acc_naive:.4f} | SVs {naive.n_support} | {t_naive*1e3:.0f} ms")
    print(f"  sklearn   train acc {sk.score(X_tr, y_tr):.4f} "
          f"| test acc {acc_sk:.4f} | SVs {sk.n_support_.sum()} | {t_sk*1e3:.0f} ms")
    return acc_naive, acc_sk, chance


if __name__ == "__main__":
    print("=== Naive SVM (simplified SMO) vs sklearn SVC on Iris binary pairs ===")
    for kernel in ("linear", "rbf"):
        for pair in ((0, 1), (1, 2), (0, 2)):
            compare(pair=pair, kernel=kernel)
