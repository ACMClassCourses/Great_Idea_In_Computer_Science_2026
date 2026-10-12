"""Atmospheric-light estimation for Dark Channel Prior dehazing."""

from __future__ import annotations

import math

import numpy as np

from ._validation import require_gray_float, require_rgb_float


def estimate_atmospheric_light(
    image: np.ndarray,
    dark: np.ndarray,
    top_percent: float = 0.001,
) -> np.ndarray:
    """Estimate an RGB atmospheric-light vector.

    Candidate pixels are the brightest ``top_percent`` of the dark channel.
    Among them, the pixel with the greatest RGB intensity in the input image
    is returned, following the standard DCP procedure.
    """
    rgb = require_rgb_float(image)
    dark_array = require_gray_float(dark, name="dark")
    if dark_array.shape != rgb.shape[:2]:
        raise ValueError("dark must have the same height and width as image")
    if not 0.0 < top_percent <= 1.0:
        raise ValueError("top_percent must lie in (0, 1]")

    # TODO 2（学生实现）：估计全局大气光 A。
    # 要求：从暗通道中选出最亮的 top_percent 像素作为候选；回到原 RGB
    # 图像，在候选中选取 RGB 强度和最大的像素。返回 shape=(3,) 的
    # float64 数组，并保证三个分量均大于 0，避免后续除零。
    raise NotImplementedError("TODO 2: implement atmospheric-light estimation")
