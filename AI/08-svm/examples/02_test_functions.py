"""Example 2 – validate the from-scratch GA and PSO on the Sphere function.

Minimise f(x) = sum x_j^2, x in [-5.12, 5.12]^10 (global optimum 0 at origin).
Checks per seed: monotonic best-so-far history (elitism / global-best records),
positions inside bounds, and reproducibility under a fixed seed.

Run:  python examples/02_test_functions.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402

from svmswarm.ga import GA  # noqa: E402
from svmswarm.pso import PSO  # noqa: E402

DIM = 10
BOUNDS = np.tile([-5.12, 5.12], (DIM, 1))


def sphere(x: np.ndarray) -> float:
    return float(np.sum(np.square(x)))


def run(method: str, budget: int, seeds=(0, 1, 2)):
    print(f"\n{method} on Sphere(dim={DIM}), budget={budget} evals, seeds {seeds}")
    for seed in seeds:
        opt = (PSO(n_particles=20, bounds=BOUNDS, random_state=seed) if method == "PSO"
               else GA(dim=DIM, bounds=BOUNDS, n_pop=20, seed=seed))
        res = opt.optimize(sphere, budget)
        hist = res.history
        monotone = bool(np.all(np.diff(hist[:, 1]) <= 1e-12)) if len(hist) > 1 else True
        inside = bool(np.all(res.best_x >= BOUNDS[:, 0]) and
                      np.all(res.best_x <= BOUNDS[:, 1]))
        print(f"  seed {seed}: best={res.best_value:.6f}  evals={res.n_evals}  "
              f"monotone={monotone}  inside_bounds={inside}")


def check_reproducible(method: str, budget: int):
    """Same seed => identical trajectory."""
    def one(seed):
        opt = (PSO(n_particles=20, bounds=BOUNDS, random_state=seed) if method == "PSO"
               else GA(dim=DIM, bounds=BOUNDS, n_pop=20, seed=seed))
        res = opt.optimize(sphere, budget)
        return res.best_value, res.history[-1, 1]
    a, b = one(7), one(7)
    print(f"reproducibility {method}: {a == b}")


if __name__ == "__main__":
    run("PSO", 2000)
    run("GA", 2000)
    check_reproducible("PSO", 500)
    check_reproducible("GA", 500)
    print("\nExpected: best values clearly below 1 (well below the random-start level) "
          "and monotone = True.")
