"""Command-line interface for the DCP teaching project."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

from .io import write_rgb_image
from .pipeline import DCPConfig, dehaze_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Dark Channel Prior single-image dehazing"
    )
    parser.add_argument("-i", "--input", required=True, help="input JPG/PNG path")
    parser.add_argument(
        "-o",
        "--output",
        help=(
            "output directory; an image suffix writes all intermediates to a "
            "sibling '<name>_results' directory and writes the final image here"
        ),
    )
    parser.add_argument("--window-size", type=int, default=15)
    parser.add_argument("--omega", type=float, default=0.95)
    parser.add_argument("--top-percent", type=float, default=0.001)
    parser.add_argument("--guided-radius", type=int, default=40)
    parser.add_argument("--guided-epsilon", type=float, default=1e-3)
    parser.add_argument("--t0", type=float, default=0.1)
    parser.add_argument(
        "--no-refine",
        action="store_true",
        help="use raw transmission without guided filtering",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="open input and result windows after processing",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    input_path = Path(args.input)
    output_dir, requested_image = _resolve_output(input_path, args.output)
    config = DCPConfig(
        window_size=args.window_size,
        omega=args.omega,
        atmospheric_top_percent=args.top_percent,
        guided_radius=args.guided_radius,
        guided_epsilon=args.guided_epsilon,
        transmission_floor=args.t0,
        refine=not args.no_refine,
    )

    try:
        result, paths = dehaze_file(input_path, output_dir, config)
    except (FileNotFoundError, OSError, TypeError, ValueError) as error:
        raise SystemExit(f"error: {error}") from error

    if requested_image is not None:
        write_rgb_image(requested_image, result.dehazed_image)

    print(f"Results written to: {output_dir.resolve()}")
    print(
        "Atmospheric light (RGB): "
        + np.array2string(result.atmospheric_light, precision=4)
    )

    if args.show:
        source_bgr = cv2.cvtColor(
            np.rint(result.input_image * 255.0).astype(np.uint8),
            cv2.COLOR_RGB2BGR,
        )
        result_bgr = cv2.cvtColor(
            np.rint(result.dehazed_image * 255.0).astype(np.uint8),
            cv2.COLOR_RGB2BGR,
        )
        cv2.imshow("input", source_bgr)
        cv2.imshow("dehazed", result_bgr)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return 0


def _resolve_output(input_path: Path, output: str | None) -> tuple[Path, Path | None]:
    if output is None:
        return Path("outputs") / input_path.stem, None
    requested = Path(output)
    if requested.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}:
        directory = requested.parent / f"{requested.stem}_results"
        return directory, requested
    return requested, None
