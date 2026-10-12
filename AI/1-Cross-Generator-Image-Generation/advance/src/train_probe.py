"""Student task: train only on Train-A CLIP features and evaluate held-out splits."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

from utils import metrics


def fit_probe(X: np.ndarray, y: np.ndarray, splits: np.ndarray, seed: int):
    """Fit a balanced linear probe using only rows whose split is train."""
    # TODO 7: Select only split == "train", verify both labels exist, create
    # LogisticRegression(max_iter=2000, random_state=seed,
    # class_weight="balanced"), fit it, and return it. CLIP is not updated.
    raise NotImplementedError("TODO 7: fit the Train-A linear probe")


def evaluate_splits(y: np.ndarray, probabilities: np.ndarray, splits: np.ndarray):
    """Compute separate Dev-A, Test-A, and Test-B metrics."""
    # TODO 8: For each required split, select its rows and call metrics().
    # Reject a missing split. Print n, accuracy, F1, and AUROC separately and
    # return a dictionary keyed by split name. Never merge Test-A and Test-B.
    raise NotImplementedError("TODO 8: evaluate all held-out splits")


def save_outputs(output_dir: Path, data_root: Path | None, error_count: int,
                 y, probabilities, paths, sources, splits, results) -> None:
    """Save metrics, every prediction, and the most confident Test-B errors."""
    # TODO 9: Save metrics.json and predictions.csv. Select incorrect test_b
    # rows, rank them by abs(P(synthetic)-0.5), and save at most error_count to
    # errors_test_b.csv. If data_root is supplied, also copy those images to
    # output_dir/error_images. See README for the required CSV columns.
    raise NotImplementedError("TODO 9: save predictions and Test-B errors")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--data-root", type=Path)
    parser.add_argument("--error-count", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    bundle = np.load(args.features)
    X, y = bundle["features"], bundle["labels"]
    paths, sources, splits = bundle["paths"], bundle["sources"], bundle["splits"]
    if X.ndim != 2 or X.shape[1] != 512:
        raise SystemExit(f"Expected 512-D CLIP features, got {X.shape}")
    probe = fit_probe(X, y, splits, args.seed)
    probabilities = probe.predict_proba(X)[:, 1]
    results = evaluate_splits(y, probabilities, splits)
    save_outputs(args.output_dir, args.data_root, args.error_count,
                 y, probabilities, paths, sources, splits, results)


if __name__ == "__main__":
    main()
