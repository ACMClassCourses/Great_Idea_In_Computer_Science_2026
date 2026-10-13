#!/usr/bin/env python3
"""Project 9 Basic starter: timestamp-aligned, strictly past-only baselines."""
from __future__ import annotations

import sys


def audit_and_sort(rows: list[tuple[int, float]]) -> list[tuple[int, float]]:
    """Sort timestamps and reject duplicates. Missing hours are allowed and recorded by callers."""
    # TODO: sort, check duplicate timestamps, and return a new list.
    raise NotImplementedError


def predict(rows: list[tuple[int, float]]) -> list[tuple[int, float, float, float]]:
    """Return test-hour predictions: (hour, day, week, trailing_24h_mean)."""
    # TODO:
    # 1. test_start = floor(0.8 * n)
    # 2. look up hour-24/hour-168 by timestamp, never by row offset
    # 3. calculate the fallback from known rows with hour-24 <= h < hour
    # 4. use only rows strictly earlier than the target hour
    raise NotImplementedError


def solve(tokens: list[str]):
    count = int(tokens[0])
    rows = [(int(tokens[1 + 2 * i]), float(tokens[2 + 2 * i])) for i in range(count)]
    ordered = audit_and_sort(rows)
    return predict(ordered)


if __name__ == "__main__":
    predictions = solve(sys.stdin.read().split())
    values = [str(len(predictions))]
    for hour, day, week, mean24 in predictions:
        values.extend((str(hour), f"{day:.10f}", f"{week:.10f}", f"{mean24:.10f}"))
    print(" ".join(values))
