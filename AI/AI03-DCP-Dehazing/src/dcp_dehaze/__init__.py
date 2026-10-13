"""Teaching-oriented implementation of Dark Channel Prior dehazing."""

from .airlight import estimate_atmospheric_light
from .dark_channel import dark_channel
from .io import read_image_rgb, write_gray_png, write_rgb_image, write_rgb_png
from .pipeline import DCPConfig, DehazeResult, dehaze_file, dehaze_image
from .recovery import recover_scene
from .transmission import estimate_transmission, guided_filter, refine_transmission

__all__ = [
    "DCPConfig",
    "DehazeResult",
    "dark_channel",
    "dehaze_file",
    "dehaze_image",
    "estimate_atmospheric_light",
    "estimate_transmission",
    "guided_filter",
    "read_image_rgb",
    "recover_scene",
    "refine_transmission",
    "write_gray_png",
    "write_rgb_image",
    "write_rgb_png",
]
