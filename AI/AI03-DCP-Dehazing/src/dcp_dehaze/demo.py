"""Deterministic synthetic scene used by the offline project demo."""

from __future__ import annotations

import cv2
import numpy as np


def create_synthetic_scene(
    width: int = 320,
    height: int = 240,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return clear RGB image, depth, and a physically hazed RGB image."""
    if width < 64 or height < 64:
        raise ValueError("demo dimensions must both be at least 64 pixels")

    clear = np.zeros((height, width, 3), dtype=np.float64)
    horizon = int(height * 0.45)

    sky_y = np.linspace(0.0, 1.0, horizon, dtype=np.float64)[:, None, None]
    sky_top = np.array([0.35, 0.58, 0.88], dtype=np.float64)
    sky_bottom = np.array([0.72, 0.80, 0.88], dtype=np.float64)
    clear[:horizon] = sky_top * (1.0 - sky_y) + sky_bottom * sky_y

    ground_y = np.linspace(0.0, 1.0, height - horizon, dtype=np.float64)[
        :, None, None
    ]
    ground_far = np.array([0.34, 0.43, 0.22], dtype=np.float64)
    ground_near = np.array([0.12, 0.28, 0.10], dtype=np.float64)
    clear[horizon:] = ground_far * (1.0 - ground_y) + ground_near * ground_y

    image = clear
    cv2.rectangle(
        image,
        (int(width * 0.08), int(height * 0.42)),
        (int(width * 0.28), int(height * 0.72)),
        (0.55, 0.18, 0.12),
        thickness=-1,
    )
    cv2.rectangle(
        image,
        (int(width * 0.12), int(height * 0.50)),
        (int(width * 0.17), int(height * 0.62)),
        (0.06, 0.08, 0.10),
        thickness=-1,
    )
    cv2.rectangle(
        image,
        (int(width * 0.21), int(height * 0.50)),
        (int(width * 0.25), int(height * 0.62)),
        (0.92, 0.78, 0.25),
        thickness=-1,
    )
    for fraction, radius in ((0.56, 15), (0.68, 22), (0.84, 30)):
        center = (int(width * fraction), int(height * (0.54 + 0.22 * fraction)))
        cv2.rectangle(
            image,
            (center[0] - 3, center[1]),
            (center[0] + 3, center[1] + radius * 2),
            (0.18, 0.10, 0.05),
            thickness=-1,
        )
        cv2.circle(image, center, radius, (0.03, 0.22, 0.06), thickness=-1)

    road = np.array(
        [
            [int(width * 0.44), height - 1],
            [int(width * 0.60), horizon],
            [int(width * 0.68), horizon],
            [int(width * 0.85), height - 1],
        ],
        dtype=np.int32,
    )
    cv2.fillConvexPoly(image, road, (0.18, 0.18, 0.20))

    y = np.linspace(0.0, 1.0, height, dtype=np.float64)[:, None]
    depth = np.repeat(5.0 - 4.2 * y, width, axis=1)
    depth[horizon:] *= 0.85
    beta = 0.32
    transmission = np.exp(-beta * depth)
    atmospheric_light = np.array([0.86, 0.91, 0.98], dtype=np.float64)
    hazy = image * transmission[..., None] + atmospheric_light * (
        1.0 - transmission[..., None]
    )
    return np.clip(image, 0.0, 1.0), depth, np.clip(hazy, 0.0, 1.0)

