"""Dark-channel computation."""

from __future__ import annotations

import cv2
import numpy as np

from ._validation import require_odd_window, require_rgb_float


def dark_channel(
    image: np.ndarray,
    window_size: int = 15,
    *,
    require_unit_range: bool = True,
) -> np.ndarray:
    """Compute the dark channel of a normalized RGB image.

    The operation first takes the minimum across RGB channels and then applies
    a local minimum filter using morphological erosion.
    """
    rgb = require_rgb_float(image, require_unit_range=require_unit_range)
    size = require_odd_window(window_size)

    # TODO 1（学生实现）：计算暗通道。
    # 要求：先求每个像素三个颜色通道的最小值，再在 size × size
    # 邻域内执行局部最小值滤波。建议使用 NumPy 与 cv2.erode；边界采用
    # cv2.BORDER_REPLICATE。返回形状应为 (H, W)，且不得修改输入数组。
    raise NotImplementedError("TODO 1: implement dark-channel computation")
