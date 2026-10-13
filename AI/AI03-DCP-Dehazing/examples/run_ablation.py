"""Run a small, reproducible one-factor-at-a-time DCP ablation study."""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import replace
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from dcp_dehaze.pipeline import DCPConfig, dehaze_file  # noqa: E402


EXPERIMENTS = [
    ("baseline", {}),
    ("window_7", {"window_size": 7}),
    ("window_31", {"window_size": 31}),
    ("omega_080", {"omega": 0.80}),
    ("omega_100", {"omega": 1.00}),
    ("t0_005", {"transmission_floor": 0.05}),
    ("t0_020", {"transmission_floor": 0.20}),
    ("no_refine", {"refine": False}),
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("outputs/ablation"))
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    baseline = DCPConfig()
    rows: list[dict[str, object]] = []
    for name, changes in EXPERIMENTS:
        config = replace(baseline, **changes)
        result, _ = dehaze_file(args.input, args.output / name, config)
        rows.append(
            {
                "experiment": name,
                "window_size": config.window_size,
                "omega": config.omega,
                "transmission_floor": config.transmission_floor,
                "refine": config.refine,
                "airlight_r": result.atmospheric_light[0],
                "airlight_g": result.atmospheric_light[1],
                "airlight_b": result.atmospheric_light[2],
                "transmission_min": result.refined_transmission.min(),
                "transmission_max": result.refined_transmission.max(),
            }
        )

    summary_path = args.output / "summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Ablation results written to: {args.output.resolve()}")


if __name__ == "__main__":
    main()

