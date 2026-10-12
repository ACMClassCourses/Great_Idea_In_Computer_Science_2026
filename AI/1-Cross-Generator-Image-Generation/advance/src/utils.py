"""Provided helpers: students do not need to modify this file."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score

FIELDS = ("path", "label", "source", "split")
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"Manifest is empty: {path}")
    missing = set(FIELDS) - set(rows[0])
    if missing:
        raise SystemExit(f"Manifest is missing columns: {sorted(missing)}")
    return [{key: row[key] for key in FIELDS} for row in rows]


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def metrics(y_true: np.ndarray, probabilities: np.ndarray) -> dict[str, float | int]:
    predictions = (probabilities >= 0.5).astype(np.int64)
    result: dict[str, float | int] = {
        "samples": int(len(y_true)),
        "accuracy": float(accuracy_score(y_true, predictions)),
        "precision": float(precision_score(y_true, predictions, zero_division=0)),
        "recall": float(recall_score(y_true, predictions, zero_division=0)),
        "f1": float(f1_score(y_true, predictions, zero_division=0)),
    }
    result["auroc"] = (
        float(roc_auc_score(y_true, probabilities)) if len(np.unique(y_true)) == 2 else float("nan")
    )
    return result


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
