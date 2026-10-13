"""Basic: minimal real/synthetic detector (STUDENT VERSION).

Fill in every block marked ``TODO``. The goal is the simplest possible
detector: images -> grayscale 32x32 -> pixels as one vector -> logistic
regression -> real / synthetic.

Data layout:
    data/raw/real/<source_name>/*.jpg
    data/raw/synthetic/<generator_name>/*.png

Run:
    python train_binary.py --input data/raw

The handout checklist (section 3):
    1. read images and unify the size
    2. split train/test by FILE (~8:2); no test image may appear in train
    3. train the simplest detector (logistic regression on flattened pixels)
    4. print train accuracy, test accuracy, test sample count, generator name
    5. print predictions for a few unseen test images
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
LABELS = ("real", "synthetic")
IMAGE_SIZE = 32


def iter_samples(root: Path):
    """Yield (path, label, source_name) for every image under ``root``.

    label  -> top folder name: "real" or "synthetic"
    source -> next folder name: dataset / generator name
    """
    # TODO 1: walk root/real/<source>/* and root/synthetic/<source>/* and
    #         yield (path, label, source) for every image file.
    #         Hint: use ``path.suffix.lower() in IMAGE_SUFFIXES`` to filter.
    raise NotImplementedError("TODO 1: implement iter_samples")


def load_image(path: Path, size: int = IMAGE_SIZE) -> np.ndarray:
    """Open an image, convert to grayscale, resize, and flatten to one vector."""
    # TODO 2: open with PIL, convert("L"), resize((size, size)),
    #         divide by 255.0, then .reshape(-1) into a 1-D float vector.
    raise NotImplementedError("TODO 2: implement load_image")


def split_samples(samples, test_ratio: float, seed: int):
    """Split by file: reproducible shuffle, then hold out a test fraction."""
    # TODO 3: shuffle a COPY with random.Random(seed), then return
    #         (train, test) where test is about test_ratio of the files.
    #         Make sure no file is in both lists.
    raise NotImplementedError("TODO 3: implement split_samples")


def build_features(samples, size: int):
    """Stack flattened pixels into X and labels into y (synthetic -> 1)."""
    # TODO 4: return (X, y) where
    #         X = np.stack([...load_image...]) and
    #         y = 1 for "synthetic", 0 for "real".
    raise NotImplementedError("TODO 4: implement build_features")


def main() -> None:
    parser = argparse.ArgumentParser(description="Basic minimal detector")
    parser.add_argument("--input", type=Path, required=True, help="data/raw directory")
    parser.add_argument("--test-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--image-size", type=int, default=IMAGE_SIZE)
    args = parser.parse_args()

    samples = list(iter_samples(args.input))
    if len(samples) < 2:
        raise SystemExit(
            f"No images found under {args.input}. Expected "
            f"{args.input}/real/<source>/* and {args.input}/synthetic/<generator>/*"
        )

    train, test = split_samples(samples, args.test_ratio, args.seed)
    X_train, y_train = build_features(train, args.image_size)
    X_test, y_test = build_features(test, args.image_size)

    # TODO 5: create the one-neuron classifier, fit it on the training pixels,
    #         then compute train/test accuracy with accuracy_score.
    #         (LogisticRegression(max_iter=1000, random_state=args.seed))
    raise NotImplementedError("TODO 5: train and evaluate the detector")

    # After TODO 5 works, fill in the result output below.
    generators = sorted({source for _, label, source in samples if label == "synthetic"})
    print(f"Generator(s)   : {', '.join(generators) if generators else '(none found)'}")
    print(f"Train samples  : {len(train)}")
    print(f"Test samples   : {len(test)}")
    # TODO 6: print train accuracy, test accuracy.
    # TODO 7: print predictions and P(synthetic) for a few unseen test images.
    #         Class 1 probability is classifier.predict_proba(X_test)[:, 1].


if __name__ == "__main__":
    main()
