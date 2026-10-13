#!/usr/bin/env python3
"""Project 3 Basic starter. Keep the public function signatures unchanged."""
from __future__ import annotations

import math
import sys
import numpy as np


def dark_channel(image: np.ndarray, window: int) -> np.ndarray:
    """Return min over RGB, then local window; use replicated borders."""
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("image must have shape [H,W,3]")
    if window <= 0 or window % 2 == 0:
        raise ValueError("window must be a positive odd integer")
    # TODO: channel minimum followed by a local minimum filter.
    raise NotImplementedError


def estimate_airlight(image: np.ndarray, dark: np.ndarray) -> np.ndarray:
    """Use top 0.1% dark pixels, then maximum RGB sum; stable row-major ties."""
    # TODO: return a length-3 vector.
    raise NotImplementedError


def estimate_transmission(image: np.ndarray, airlight: np.ndarray,
                          window: int, omega: float, t0: float) -> np.ndarray:
    """Compute t_raw from dark(I/A), clip to [0,1], then apply t0."""
    # TODO: protect every component of A by epsilon=1e-6.
    raise NotImplementedError


def recover(image: np.ndarray, airlight: np.ndarray,
            transmission: np.ndarray) -> np.ndarray:
    """Recover J and clip only the returned image to [0,1]."""
    # TODO: broadcast A over pixels and t over RGB channels.
    raise NotImplementedError


def solve(tokens: list[str]) -> np.ndarray:
    iterator = iter(tokens)
    height, width, window = int(next(iterator)), int(next(iterator)), int(next(iterator))
    omega, t0 = float(next(iterator)), float(next(iterator))
    values = [float(next(iterator)) for _ in range(height * width * 3)]
    image = np.asarray(values, dtype=np.float64).reshape(height, width, 3)
    dark = dark_channel(image, window)
    airlight = estimate_airlight(image, dark)
    transmission = estimate_transmission(image, airlight, window, omega, t0)
    recovered = recover(image, airlight, transmission)
    return np.concatenate((airlight.ravel(), dark.ravel(), transmission.ravel(), recovered.ravel()))


if __name__ == "__main__":
    answer = solve(sys.stdin.read().split())
    print(" ".join(f"{value:.10f}" for value in answer))
