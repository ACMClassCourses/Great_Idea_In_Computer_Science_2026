"""Scene-radiance recovery."""

from __future__ import annotations

import numpy as np

from ._validation import require_gray_float, require_rgb_float


def recover_scene(
    image: np.ndarray,
    atmospheric_light: np.ndarray,
    transmission: np.ndarray,
    *,
    transmission_floor: float = 0.1,
) -> np.ndarray:
    """Recover and clip scene radiance according to the scattering model."""
    rgb = require_rgb_float(image)
    airlight = np.asarray(atmospheric_light, dtype=np.float64)
    trans = require_gray_float(transmission, name="transmission")
    if airlight.shape != (3,):
        raise ValueError("atmospheric_light must contain exactly three values")
    if not np.all(np.isfinite(airlight)):
        raise ValueError("atmospheric_light contains invalid values")
    if trans.shape != rgb.shape[:2]:
        raise ValueError("transmission must match the image height and width")
    if not 0.0 < transmission_floor <= 1.0:
        raise ValueError("transmission_floor must lie in (0, 1]")

    # TODO 6（学生实现）：根据大气散射模型恢复无雾图像。
    # 先用 transmission_floor 限制透射率下界，再按 README 中的反演公式
    # 对三个颜色通道进行向量化计算。最终输出应裁剪至 [0, 1]。
    raise NotImplementedError("TODO 6: implement scene-radiance recovery")
