"""Student task: build a source-isolated Train-A / Dev-A / Test-A / Test-B manifest."""

from __future__ import annotations

import argparse
import random
from collections import Counter
from pathlib import Path

from utils import IMAGE_SUFFIXES, write_manifest


def scan(directory: Path, root: Path, label: str, source: str) -> list[dict[str, str]]:
    """Return one record per supported image below directory."""
    # TODO 1: Verify the directory exists, recursively find supported images,
    # and return path/label/source/split records. Store each path relative to
    # root and use an empty string as its initial split.
    raise NotImplementedError("TODO 1: scan image sources")


def partition(items: list[dict[str, str]], counts: tuple[int, ...], rng: random.Random):
    shuffled = list(items)
    rng.shuffle(shuffled)
    parts, start = [], 0
    for count in counts:
        parts.append(shuffled[start : start + count])
        start += count
    parts.append(shuffled[start:])
    return parts


def tag(items: list[dict[str, str]], split: str) -> list[dict[str, str]]:
    return [{**item, "split": split} for item in items]


def build_and_validate_rows(args: argparse.Namespace) -> list[dict[str, str]]:
    """Split sources and reject leakage before returning manifest rows."""
    # TODO 2:
    # 1. Require different A/B generators and different train/test real sources.
    # 2. Scan the four selected source directories.
    # 3. Build class-balanced train/dev_a/test_a/test_b splits. Split
    #    train-real into train/dev_a; split A into train/dev_a/test_a; put B
    #    only in test_b. It is fine to leave surplus images unused.
    # 4. Put the same sampled test-real records in test_a and test_b.
    # 5. Assert generator B never occurs in train/dev and no train/dev path
    #    occurs in either test split. Every split must contain both labels.
    raise NotImplementedError("TODO 2: build and validate source-isolated splits")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--train-gen", required=True)
    parser.add_argument("--test-gen", required=True)
    parser.add_argument("--train-real-source", required=True)
    parser.add_argument("--test-real-source", required=True)
    parser.add_argument("--dev-ratio", type=float, default=0.1)
    parser.add_argument("--test-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    rows = build_and_validate_rows(args)
    rows.sort(key=lambda row: (row["split"], row["label"], row["path"]))
    write_manifest(args.output, rows)
    counts = Counter((row["split"], row["label"]) for row in rows)
    print(f"Wrote {len(rows)} records to {args.output}")
    for split in ("train", "dev_a", "test_a", "test_b"):
        print(f"{split:7} real={counts[(split, 'real')]:4} synthetic={counts[(split, 'synthetic')]:4}")


if __name__ == "__main__":
    main()
