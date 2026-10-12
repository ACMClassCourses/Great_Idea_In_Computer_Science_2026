"""Example 4 – formal multi-seed MADELON experiments (README deliverable).

Budget B=200, K=5, 5 seeds for GA / hybrid PSO / random search, plus default SVM,
the keep-all-features ablation, the PSO inertia-decay ablation and the lambda
sensitivity ablation.  Expect roughly one to two hours of wall time depending on
the machine; run it in the background.

Run:  python examples/04_full_experiment.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from svmswarm.config import full_config  # noqa: E402
from svmswarm.experiment import run_experiment  # noqa: E402

if __name__ == "__main__":
    cfg = full_config()
    print(f"Full experiment: budget={cfg.budget}, K={cfg.n_splits}, "
          f"seeds={cfg.seeds}")
    out = run_experiment(cfg)
    print(f"\nOutputs written to: {out}")
    print(f"Report: {out / 'report.md'}")
