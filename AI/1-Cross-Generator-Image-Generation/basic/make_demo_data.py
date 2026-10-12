"""Generate a tiny demo dataset so the Basic pipeline can be smoke-tested.

This is NOT real data and must NOT be used in the final submission. The real
Basic task uses a public dataset such as CIFAKE (one generator) laid out as:

    data/raw/real/<source_name>/*.jpg
    data/raw/synthetic/<generator_name>/*.png

The demo images here only exist so that students can check that
``train_binary.py`` runs end to end before downloading real data.

Usage:
    python make_demo_data.py                 # writes 50 + 50 images
    python make_demo_data.py --per-class 20
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

DEMO_REAL_SOURCE = "demo_photos"
DEMO_SYNTHETIC_GENERATOR = "demo_gen"
IMAGE_SIZE = 64


def make_real(rng: np.random.Generator, size: int) -> np.ndarray:
    """Smooth low-frequency image with little high-frequency detail."""
    yy, xx = np.mgrid[0:size, 0:size] / float(size)
    image = rng.uniform(0.3, 0.7)
    image = image + 0.15 * np.sin(2 * np.pi * xx * rng.uniform(0.5, 1.5))
    image = image + 0.15 * np.cos(2 * np.pi * yy * rng.uniform(0.5, 1.5))
    for _ in range(rng.integers(0, 2)):
        cy, cx = rng.uniform(0, size, 2)
        radius = rng.uniform(size * 0.15, size * 0.35)
        blob = np.exp(-(((yy * size - cy) ** 2 + (xx * size - cx) ** 2) / (2 * radius**2)))
        image = image + rng.uniform(-0.2, 0.2) * blob
    image = image + rng.normal(0.0, 0.02, image.shape)
    return np.clip(image, 0.0, 1.0)


def make_synthetic(rng: np.random.Generator, size: int) -> np.ndarray:
    """Add a strong high-frequency grid, which a detector can pick up."""
    yy, xx = np.mgrid[0:size, 0:size]
    period = int(rng.integers(2, 5))
    checker = ((xx // period + yy // period) % 2).astype(np.float32)
    image = 0.4 + 0.35 * checker
    image = image + rng.uniform(-0.1, 0.1)
    image = image + rng.normal(0.0, 0.05, image.shape)
    return np.clip(image, 0.0, 1.0)


def save(image: np.ndarray, path: Path, fmt: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    array = (image * 255.0).round().astype(np.uint8)
    Image.fromarray(array, mode="L").save(path, format=fmt)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/raw"))
    parser.add_argument("--per-class", type=int, default=50)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    real_dir = args.output / "real" / DEMO_REAL_SOURCE
    fake_dir = args.output / "synthetic" / DEMO_SYNTHETIC_GENERATOR

    for index in range(args.per_class):
        save(make_real(rng, IMAGE_SIZE), real_dir / f"real_{index:04d}.jpg", "JPEG")
        save(make_synthetic(rng, IMAGE_SIZE), fake_dir / f"fake_{index:04d}.png", "PNG")

    print(f"Wrote {args.per_class} real images to {real_dir}")
    print(f"Wrote {args.per_class} synthetic images to {fake_dir}")
    print("Reminder: this demo data is only for smoke-testing, not for submission.")


if __name__ == "__main__":
    main()
