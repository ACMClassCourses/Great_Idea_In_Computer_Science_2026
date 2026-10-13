"""Unicode-safe image input and output helpers for Windows and other systems."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from ._validation import require_gray_float, require_rgb_float


def read_image_rgb(path: str | Path) -> np.ndarray:
    """Read an image as a normalized float64 RGB array.

    ``cv2.imdecode`` is used instead of ``cv2.imread`` so paths containing
    non-ASCII characters work reliably on Windows.
    """
    image_path = Path(path)
    if not image_path.is_file():
        raise FileNotFoundError(f"input image does not exist: {image_path}")

    encoded = np.fromfile(image_path, dtype=np.uint8)
    decoded = cv2.imdecode(encoded, cv2.IMREAD_UNCHANGED)
    if decoded is None:
        raise ValueError(f"OpenCV could not decode the image: {image_path}")

    if decoded.ndim == 2:
        rgb = cv2.cvtColor(decoded, cv2.COLOR_GRAY2RGB)
    elif decoded.ndim == 3 and decoded.shape[2] == 3:
        rgb = cv2.cvtColor(decoded, cv2.COLOR_BGR2RGB)
    elif decoded.ndim == 3 and decoded.shape[2] == 4:
        rgb = cv2.cvtColor(decoded, cv2.COLOR_BGRA2RGB)
    else:
        raise ValueError(f"unsupported image shape: {decoded.shape}")

    if rgb.dtype == np.uint8:
        scale = 255.0
    elif rgb.dtype == np.uint16:
        scale = 65535.0
    else:
        rgb = rgb.astype(np.float64)
        maximum = float(np.max(rgb)) if rgb.size else 0.0
        scale = maximum if maximum > 1.0 else 1.0

    return np.clip(rgb.astype(np.float64) / scale, 0.0, 1.0)


def write_rgb_png(path: str | Path, image: np.ndarray) -> Path:
    """Write a normalized RGB image as an 8-bit PNG."""
    rgb = require_rgb_float(image)
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    bgr = cv2.cvtColor(np.rint(rgb * 255.0).astype(np.uint8), cv2.COLOR_RGB2BGR)
    _encode_to_path(destination, bgr)
    return destination


def write_rgb_image(path: str | Path, image: np.ndarray) -> Path:
    """Write normalized RGB data using the destination file extension."""
    rgb = require_rgb_float(image)
    destination = Path(path)
    extension = destination.suffix.lower()
    if extension not in {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}:
        raise ValueError(f"unsupported output image extension: {extension or '<none>'}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    bgr = cv2.cvtColor(np.rint(rgb * 255.0).astype(np.uint8), cv2.COLOR_RGB2BGR)
    _encode_to_path(destination, bgr, extension)
    return destination


def write_gray_png(path: str | Path, image: np.ndarray) -> Path:
    """Write a normalized grayscale image as an 8-bit PNG."""
    gray = require_gray_float(image)
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded_image = np.rint(np.clip(gray, 0.0, 1.0) * 255.0).astype(np.uint8)
    _encode_to_path(destination, encoded_image)
    return destination


def _encode_to_path(path: Path, image: np.ndarray, extension: str = ".png") -> None:
    success, encoded = cv2.imencode(extension, image)
    if not success:
        raise OSError(f"OpenCV could not encode output: {path}")
    encoded.tofile(path)
