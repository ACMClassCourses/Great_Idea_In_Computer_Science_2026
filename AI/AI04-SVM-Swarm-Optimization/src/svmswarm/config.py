"""Experiment configurations (teaching defaults from README section 7).

``quick``  – small budget for end-to-end smoke validation.
``full``   – the formal multi-seed experiments reported in the README/report.

Both share identical data handling: fixed stratified folds (cv_seed), identical
candidate-encoding search space and per-method budget ``B`` on *candidate
evaluations*.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ExperimentConfig:
    name: str
    budget: int                 # B: candidate evaluation budget per run
    n_splits: int               # K folds of the inner stratified CV
    cv_seed: int = 42           # fixed fold random state (same for every method)
    seeds: list[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])
    penalty: float = 0.01       # lambda of J = S_CV - lambda * ||m||_0 / d
    cv_jobs: int = 4            # parallel folds inside one evaluation
    # population sizes (doc defaults)
    n_particles: int = 10
    n_pop: int = 10
    # PSO
    pso_w: float = 0.7
    pso_c1: float = 1.5
    pso_c2: float = 1.5
    pso_v_max_frac: float = 0.3
    pso_v_bin_max: float = 4.0
    # GA
    ga_tournament: int = 3
    ga_pc: float = 0.9
    ga_pm_cont: float = 0.2
    ga_mut_scale: float = 0.05
    ga_elite: int = 1
    # random search over the full space
    rs_p_mask: float = 0.2
    n_feat: int = 500
    # warm-start of GA/PSO feature masks from a one-shot univariate screen
    # (documented heuristic; a no-prior control GA-uniform separates algorithm
    #  effect from prior effect; random search stays uninformed on purpose)
    use_screening_prior: bool = True
    prior_top: int = 30            # top-ranked features receive the high probability
    prior_p_top: float = 0.8
    prior_p_rest: float = 0.005
    run_uniform_control: bool = True   # GA without screening prior (ablation A4)
    uniform_control_seeds: list[int] = field(default_factory=lambda: [0, 1, 2])
    # which experiments to run
    run_noFS_ablation: bool = True    # C/gamma-only with all 500 features
    noFS_budget: int = 100            # budget shared by the A1 pair (FS vs noFS)
    noFS_seeds: list[int] = field(default_factory=lambda: [0, 1, 2])
    run_wdecay_ablation: bool = True  # PSO linear inertia decay vs fixed w
    wdecay_budget: int = 200          # same budget as the main PSO rows
    wdecay_seeds: list[int] = field(default_factory=lambda: [0, 1, 2])


def quick_config() -> ExperimentConfig:
    return ExperimentConfig(
        name="quick",
        budget=60,
        n_splits=3,
        seeds=[0, 1, 2],
        cv_jobs=4,
        run_noFS_ablation=False,
        run_wdecay_ablation=False,
    )


def full_config() -> ExperimentConfig:
    return ExperimentConfig(
        name="full",
        budget=200,
        n_splits=5,
        seeds=[0, 1, 2, 3, 4],
        cv_jobs=4,
        run_noFS_ablation=True,
        noFS_budget=120,
        noFS_seeds=[0, 1, 2],
        run_wdecay_ablation=True,
        wdecay_budget=200,
        wdecay_seeds=[0, 1, 2],
    )
