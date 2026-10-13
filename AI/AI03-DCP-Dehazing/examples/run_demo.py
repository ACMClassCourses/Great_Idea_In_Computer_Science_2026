"""Generate a license-safe synthetic hazy image and run the full DCP pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from dcp_dehaze.demo import create_synthetic_scene  # noqa: E402
from dcp_dehaze.io import write_gray_png, write_rgb_png  # noqa: E402
from dcp_dehaze.pipeline import DCPConfig, dehaze_file  # noqa: E402


def main() -> None:
    clear, depth, hazy = create_synthetic_scene()
    input_dir = PROJECT_ROOT / "assets" / "input"
    expected_dir = PROJECT_ROOT / "assets" / "expected"
    output_dir = PROJECT_ROOT / "outputs" / "demo"

    hazy_path = write_rgb_png(input_dir / "synthetic_hazy.png", hazy)
    write_rgb_png(expected_dir / "synthetic_clear_reference.png", clear)
    write_gray_png(expected_dir / "synthetic_depth_normalized.png", depth / depth.max())

    result, paths = dehaze_file(hazy_path, output_dir, DCPConfig())
    print(f"Synthetic input: {hazy_path}")
    print(f"Demo results: {output_dir}")
    print(f"Estimated atmospheric light (RGB): {result.atmospheric_light}")
    for name, path in paths.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    main()

