"""Raw transmission estimation and edge-preserving refinement."""

from __future__ import annotations

import cv2
import numpy as np

from ._validation import require_gray_float, require_rgb_float
from .dark_channel import dark_channel


def estimate_transmission(
    image: np.ndarray,
    atmospheric_light: np.ndarray,
    *,
    window_size: int = 15,
    omega: float = 0.95,
) -> np.ndarray:
    """Estimate the coarse transmission map from a normalized RGB image."""
    rgb = require_rgb_float(image)
    airlight = np.asarray(atmospheric_light, dtype=np.float64)
    if airlight.shape != (3,):
        raise ValueError("atmospheric_light must contain exactly three values")
    if not np.all(np.isfinite(airlight)) or np.any(airlight <= 0.0):
        raise ValueError("atmospheric_light must contain finite positive values")
    if not 0.0 < omega <= 1.0:
        raise ValueError("omega must lie in (0, 1]")

    # TODO 3（学生实现）：依据暗通道先验估计粗透射率。
    # 先按颜色通道计算 I / A，再对该比值图计算暗通道，最后代入 README
    # 中的透射率公式。注意 I / A 可能大于 1；输出需裁剪至 [0, 1]。
    raise NotImplementedError("TODO 3: implement coarse transmission estimation")


def guided_filter(
    guidance: np.ndarray,
    source: np.ndarray,
    *,
    radius: int = 40,
    epsilon: float = 1e-3,
) -> np.ndarray:
    """Apply a grayscale guided filter.

    ``radius`` is the pixel radius, so the box-filter kernel size is
    ``2 * radius + 1``. Both inputs must be two-dimensional float arrays.
    """
    guide = require_gray_float(guidance, name="guidance").astype(np.float64)
    src = require_gray_float(source, name="source").astype(np.float64)
    if guide.shape != src.shape:
        raise ValueError("guidance and source must have the same shape")
    if isinstance(radius, bool) or not isinstance(radius, (int, np.integer)):
        raise TypeError("radius must be an integer")
    if radius < 0:
        raise ValueError("radius must be non-negative")
    if epsilon <= 0.0 or not np.isfinite(epsilon):
        raise ValueError("epsilon must be finite and positive")
    # TODO 4（学生实现）：实现灰度导向滤波。
    # 使用半径 radius 对应的 (2 * radius + 1) 方框窗口，计算 guidance
    # 和 source 的局部均值、方差与协方差，再求线性系数 a、b 及最终输出。
    # 建议用 cv2.boxFilter 实现均值滤波，边界采用 cv2.BORDER_REFLECT。
    # radius == 0 时应返回 source 的副本。
    raise NotImplementedError("TODO 4: implement guided filtering")


def refine_transmission(
    image: np.ndarray,
    transmission: np.ndarray,
    *,
    radius: int = 40,
    epsilon: float = 1e-3,
) -> np.ndarray:
    """Refine a coarse transmission map using image luminance as guidance."""
    rgb = require_rgb_float(image)
    raw = require_gray_float(transmission, name="transmission")
    if raw.shape != rgb.shape[:2]:
        raise ValueError("transmission must match the image height and width")
    # TODO 5（学生实现）：以输入图像的灰度图作为引导图，调用上面的
    # guided_filter 细化粗透射率，并把输出裁剪至 [0, 1]。
    raise NotImplementedError("TODO 5: implement transmission refinement")
