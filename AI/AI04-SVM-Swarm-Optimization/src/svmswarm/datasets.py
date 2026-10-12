"""Dataset loading utilities.

Provides
  load_iris(classes)            – one binary Iris subtask (two of the three classes)
  load_madelon()                – official MADELON training / validation subsets
  parse_iris_csv(path)          – low-level iris.data parser (also used by tests)

MADELON layout inside the repository::

    madelon/
        MADELON/madelon_train.data      (2000 x 500, space separated)
        MADELON/madelon_train.labels    (2000, +/-1)
        MADELON/madelon_valid.data      (600  x 500)
        madelon_valid.labels            (600,  +/-1)

The official test subset (1800 rows) has no public labels and is *not* used.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]

IRIS_CLASSES = ["Iris-setosa", "Iris-versicolor", "Iris-virginica"]
IRIS_FEATURE_NAMES = ["sepal length (cm)", "sepal width (cm)",
                      "petal length (cm)", "petal width (cm)"]


def _find(root: Path, name: str) -> Path:
    """Recursively locate a file by name under root (deterministic order)."""
    for path in sorted(root.rglob(name)):
        if path.is_file():
            return path
    raise FileNotFoundError(f"{name!r} not found under {root}")


def parse_iris_csv(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Parse the raw iris.data CSV into (X float array, class-name array)."""
    rows_x, rows_y = [], []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            parts = [p for p in line.split(",") if p != ""]
            if len(parts) != 5:
                continue
            rows_x.append([float(p) for p in parts[:4]])
            rows_y.append(parts[4].strip())
    return np.asarray(rows_x, dtype=float), np.asarray(rows_y)


def load_iris(classes: tuple[int, int] = (1, 2),
              path: Path | None = None) -> tuple[np.ndarray, np.ndarray,
                                                 list[str], np.ndarray, np.ndarray]:
    """Load Iris restricted to two classes as a binary problem.

    Returns (X, y, feature_names, class_names, pair_indices) with y in {-1, +1}.
    By default the overlapping pair versicolor (1) vs virginica (2) is used so
    the task is not trivially separable; pass classes=(0, 1) for a separable one.
    """
    path = path or (REPO_ROOT / "iris.data")
    X_all, y_all = parse_iris_csv(path)
    c0, c1 = classes
    keep = np.isin(y_all, [IRIS_CLASSES[c0], IRIS_CLASSES[c1]])
    X = X_all[keep]
    y = np.where(y_all[keep] == IRIS_CLASSES[c1], 1.0, -1.0)
    return X, y, list(IRIS_FEATURE_NAMES), [IRIS_CLASSES[c0], IRIS_CLASSES[c1]], np.asarray(classes)


def _load_numeric(path: Path, kind: str) -> np.ndarray:
    try:
        arr = np.loadtxt(path, dtype=float)
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError(f"could not parse {kind} file {path}: {exc}") from exc
    return arr


def load_madelon(data_dir: Path | None = None) -> dict[str, np.ndarray]:
    """Load MADELON official training and validation subsets.

    Returns a dict with keys X_train, y_train, X_valid, y_valid. Labels are
    converted to +/-1 floats. The unlabeled test split is intentionally omitted.
    """
    data_dir = Path(data_dir) if data_dir is not None else (REPO_ROOT / "madelon")
    if not data_dir.exists():
        raise FileNotFoundError(f"MADELON directory not found: {data_dir}")

    try:
        train_data = _find(data_dir / "MADELON", "madelon_train.data")
        train_lab = _find(data_dir / "MADELON", "madelon_train.labels")
        valid_data = _find(data_dir / "MADELON", "madelon_valid.data")
        valid_lab = _find(data_dir, "madelon_valid.labels")
    except FileNotFoundError:  # fall back to any recursive match
        train_data = _find(data_dir, "madelon_train.data")
        train_lab = _find(data_dir, "madelon_train.labels")
        valid_data = _find(data_dir, "madelon_valid.data")
        valid_lab = _find(data_dir, "madelon_valid.labels")

    X_train = _load_numeric(train_data, "train data")
    y_train = _load_numeric(train_lab, "train labels")
    X_valid = _load_numeric(valid_data, "valid data")
    y_valid = _load_numeric(valid_lab, "valid labels")

    if X_train.ndim != 2 or X_train.shape[0] != len(y_train):
        raise ValueError(f"train shape mismatch: {X_train.shape} vs {y_train.shape}")
    if X_valid.ndim != 2 or X_valid.shape[0] != len(y_valid):
        raise ValueError(f"valid shape mismatch: {X_valid.shape} vs {y_valid.shape}")

    return {
        "X_train": X_train,
        "y_train": np.where(y_train > 0, 1.0, -1.0),
        "X_valid": X_valid,
        "y_valid": np.where(y_valid > 0, 1.0, -1.0),
    }
