"""Shared validation helpers used by the algorithm modules."""

from __future__ import annotations

import numpy as np


def require_rgb_float(
    image: np.ndarray,
    *,
    name: str = "image",
    require_unit_range: bool = True,
) -> np.ndarray:
    """Validate a finite, non-negative H x W x 3 floating-point image."""
    array = np.asarray(image)
    if array.ndim != 3 or array.shape[2] != 3:
        raise ValueError(f"{name} must have shape (height, width, 3)")
    if not np.issubdtype(array.dtype, np.floating):
        raise TypeError(f"{name} must use a floating-point dtype")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains NaN or infinite values")
    if array.size and float(array.min()) < 0.0:
        raise ValueError(f"{name} values must be non-negative")
    if require_unit_range and array.size and float(array.max()) > 1.0:
        raise ValueError(f"{name} values must lie in [0, 1]")
    return array


def require_gray_float(image: np.ndarray, *, name: str = "image") -> np.ndarray:
    """Validate an H x W finite floating-point array."""
    array = np.asarray(image)
    if array.ndim != 2:
        raise ValueError(f"{name} must have shape (height, width)")
    if not np.issubdtype(array.dtype, np.floating):
        raise TypeError(f"{name} must use a floating-point dtype")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains NaN or infinite values")
    return array


def require_odd_window(window_size: int) -> int:
    """Return a validated positive odd window size."""
    if isinstance(window_size, bool) or not isinstance(window_size, (int, np.integer)):
        raise TypeError("window_size must be an integer")
    value = int(window_size)
    if value <= 0 or value % 2 == 0:
        raise ValueError("window_size must be a positive odd integer")
    return value
