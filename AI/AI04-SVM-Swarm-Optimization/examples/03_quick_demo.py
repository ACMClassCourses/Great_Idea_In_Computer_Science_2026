"""Example 3 – quick end-to-end MADELON demo (small budget).

Validates the whole pipeline (data -> leak-free CV objective -> GA / hybrid PSO /
random search -> sealed validation evaluation) in a few minutes.  The formal
multi-seed experiments live in examples/04_full_experiment.py.

Run:  python examples/03_quick_demo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from svmswarm.config import quick_config  # noqa: E402
from svmswarm.experiment import run_experiment  # noqa: E402

if __name__ == "__main__":
    cfg = quick_config()
    print(f"Quick demo: budget={cfg.budget}, K={cfg.n_splits}, seeds={cfg.seeds}")
    out = run_experiment(cfg)
    print(f"\nOutputs written to: {out}")
    print(f"Report: {out / 'report.md'}")
