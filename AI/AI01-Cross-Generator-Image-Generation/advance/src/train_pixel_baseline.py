"""Provided Basic baseline: 32x32 grayscale pixels plus logistic regression."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.linear_model import LogisticRegression

from utils import metrics, read_manifest, write_json


def pixels(path: Path, size: int) -> np.ndarray:
    with Image.open(path) as image:
        array = np.asarray(image.convert("L").resize((size, size)), dtype=np.float32) / 255.0
    return array.reshape(-1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--image-size", type=int, default=32)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    rows = read_manifest(args.manifest)
    X = np.stack([pixels(args.data_root / row["path"], args.image_size) for row in rows])
    y = np.asarray([row["label"] == "synthetic" for row in rows], dtype=np.int64)
    splits = np.asarray([row["split"] for row in rows])
    train = splits == "train"
    classifier = LogisticRegression(max_iter=2000, random_state=args.seed, class_weight="balanced")
    classifier.fit(X[train], y[train])
    probabilities = classifier.predict_proba(X)[:, 1]
    results = {split: metrics(y[splits == split], probabilities[splits == split])
               for split in ("dev_a", "test_a", "test_b")}
    for split, values in results.items():
        print(f"{split:7} n={values['samples']:4d}  acc={values['accuracy']:.4f}  "
              f"f1={values['f1']:.4f}  auroc={values['auroc']:.4f}")
    write_json(args.output, results)


if __name__ == "__main__":
    main()
