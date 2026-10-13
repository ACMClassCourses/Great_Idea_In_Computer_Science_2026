"""End-to-end Dark Channel Prior dehazing pipeline."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from ._validation import require_odd_window, require_rgb_float
from .airlight import estimate_atmospheric_light
from .dark_channel import dark_channel
from .io import read_image_rgb, write_gray_png, write_rgb_png
from .recovery import recover_scene
from .transmission import estimate_transmission, refine_transmission


@dataclass(frozen=True)
class DCPConfig:
    """Configuration for the DCP pipeline."""

    window_size: int = 15
    omega: float = 0.95
    atmospheric_top_percent: float = 0.001
    guided_radius: int = 40
    guided_epsilon: float = 1e-3
    transmission_floor: float = 0.1
    refine: bool = True

    def validate(self) -> None:
        require_odd_window(self.window_size)
        if not 0.0 < self.omega <= 1.0:
            raise ValueError("omega must lie in (0, 1]")
        if not 0.0 < self.atmospheric_top_percent <= 1.0:
            raise ValueError("atmospheric_top_percent must lie in (0, 1]")
        if isinstance(self.guided_radius, bool) or not isinstance(
            self.guided_radius, (int, np.integer)
        ):
            raise TypeError("guided_radius must be an integer")
        if self.guided_radius < 0:
            raise ValueError("guided_radius must be non-negative")
        if self.guided_epsilon <= 0.0 or not np.isfinite(self.guided_epsilon):
            raise ValueError("guided_epsilon must be finite and positive")
        if not 0.0 < self.transmission_floor <= 1.0:
            raise ValueError("transmission_floor must lie in (0, 1]")


@dataclass(frozen=True)
class DehazeResult:
    """Images and estimated quantities produced by a DCP run."""

    input_image: np.ndarray
    dark_channel: np.ndarray
    atmospheric_light: np.ndarray
    raw_transmission: np.ndarray
    refined_transmission: np.ndarray
    dehazed_image: np.ndarray


def dehaze_image(
    image: np.ndarray,
    config: DCPConfig | None = None,
) -> DehazeResult:
    """Run the DCP pipeline on a normalized RGB image."""
    settings = config or DCPConfig()
    settings.validate()
    rgb = require_rgb_float(image).astype(np.float64, copy=False)

    dark = dark_channel(rgb, settings.window_size)
    airlight = estimate_atmospheric_light(
        rgb,
        dark,
        settings.atmospheric_top_percent,
    )
    raw = estimate_transmission(
        rgb,
        airlight,
        window_size=settings.window_size,
        omega=settings.omega,
    )
    if settings.refine:
        refined = refine_transmission(
            rgb,
            raw,
            radius=settings.guided_radius,
            epsilon=settings.guided_epsilon,
        )
    else:
        refined = raw.copy()
    recovered = recover_scene(
        rgb,
        airlight,
        refined,
        transmission_floor=settings.transmission_floor,
    )

    return DehazeResult(
        input_image=rgb.copy(),
        dark_channel=dark,
        atmospheric_light=airlight,
        raw_transmission=raw,
        refined_transmission=refined,
        dehazed_image=recovered,
    )


def dehaze_file(
    input_path: str | Path,
    output_dir: str | Path,
    config: DCPConfig | None = None,
) -> tuple[DehazeResult, dict[str, Path]]:
    """Dehaze an image file and save all teaching-oriented intermediate output."""
    settings = config or DCPConfig()
    settings.validate()
    source_path = Path(input_path)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    image = read_image_rgb(source_path)
    result = dehaze_image(image, settings)
    elapsed = time.perf_counter() - started

    paths = {
        "input": write_rgb_png(destination / "input.png", result.input_image),
        "dark_channel": write_gray_png(
            destination / "dark_channel.png", result.dark_channel
        ),
        "raw_transmission": write_gray_png(
            destination / "transmission_raw.png", result.raw_transmission
        ),
        "refined_transmission": write_gray_png(
            destination / "transmission_refined.png", result.refined_transmission
        ),
        "dehazed": write_rgb_png(
            destination / "dehazed.png", result.dehazed_image
        ),
    }

    metadata = {
        "input_path": str(source_path.resolve()),
        "output_dir": str(destination.resolve()),
        "image_shape": list(result.input_image.shape),
        "atmospheric_light_rgb": result.atmospheric_light.tolist(),
        "dark_channel_range": _range(result.dark_channel),
        "raw_transmission_range": _range(result.raw_transmission),
        "refined_transmission_range": _range(result.refined_transmission),
        "elapsed_seconds": elapsed,
        "config": asdict(settings),
    }
    metadata_path = destination / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    paths["metadata"] = metadata_path
    return result, paths


def _range(array: np.ndarray) -> list[float]:
    return [float(np.min(array)), float(np.max(array))]

