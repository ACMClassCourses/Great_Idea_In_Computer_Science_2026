"""Plotting helpers (matplotlib Agg backend, English labels to avoid font issues)."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

_PALETTE = {"GA": "#d62728", "PSO": "#1f77b4", "RandomSearch": "#2ca02c",
            "GA-noFS": "#9467bd", "PSO-noFS": "#8c564b", "RandomSearch-noFS": "#7f7f7f",
            "Default": "#555555"}


def convergence_plot(curves: dict[str, np.ndarray], out_path: Path,
                     ylabel: str = "best objective (CV accuracy - penalty)",
                     title: str = "Convergence (best-so-far vs evaluations)"):
    """curves: method name -> (n_evals, best_value).  best_value is MAXIMISED."""
    plt.figure(figsize=(7.5, 5.2))
    for name, c in curves.items():
        if c.size == 0:
            continue
        plt.plot(c[:, 0], c[:, 1], label=name, lw=1.8,
                 color=_PALETTE.get(name, None))
    plt.xlabel("candidate evaluations used")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def score_boxplot(grouped: dict[str, list[float]], out_path: Path,
                  ylabel: str = "validation accuracy", title: str = ""):
    plt.figure(figsize=(7.5, 5.2))
    names = list(grouped)
    data = [np.asarray(v, dtype=float) for v in grouped.values()]
    bp = plt.boxplot(data, labels=names, patch_artist=True)
    for patch, name in zip(bp["boxes"], names):
        patch.set_facecolor(_PALETTE.get(name, "#bbbbbb"))
        patch.set_alpha(0.55)
    plt.ylabel(ylabel)
    if title:
        plt.title(title)
    plt.grid(alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def feature_count_bar(entries: list[tuple[str, float]], out_path: Path,
                      ylabel: str = "selected features"):
    """entries: (method label, mean feature count)."""
    names = [e[0] for e in entries]
    vals = [e[1] for e in entries]
    plt.figure(figsize=(7.5, 5.0))
    colors = [_PALETTE.get(n, "#bbbbbb") for n in names]
    plt.bar(range(len(vals)), vals, color=colors, alpha=0.8)
    plt.xticks(range(len(vals)), names)
    plt.ylabel(ylabel)
    plt.grid(alpha=0.3, axis="y")
    for i, v in enumerate(vals):
        plt.text(i, v, f"{v:.1f}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def feature_frequency_plot(selected_sets: list[np.ndarray], n_feat: int,
                           out_path: Path, known_top: tuple[int, ...] = (),
                           title: str = "Feature selection frequency across runs"):
    """Histogram of how often each feature was selected across optimisation runs."""
    freq = np.zeros(n_feat)
    for sel in selected_sets:
        freq[np.asarray(sel, dtype=int)] += 1
    plt.figure(figsize=(10, 4.6))
    plt.bar(np.arange(n_feat), freq, width=1.0, color="#4472c4", alpha=0.75)
    if known_top:
        for f in known_top:
            plt.axvline(f - 0.5, color="#e74c3c", lw=1.0, ls="--", alpha=0.7)
    plt.xlabel("feature index (0-based)")
    plt.ylabel("times selected")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    return freq


def convergence_by_method(curves: dict[str, list[np.ndarray]], out_path: Path,
                          ylabel: str = "best objective", xmax: int | None = None):
    """One curve per seed per method: method -> list of (n_evals, best) curves."""
    plt.figure(figsize=(8.0, 5.4))
    for name, seeds in curves.items():
        for s in seeds:
            if s.size:
                plt.plot(s[:, 0], s[:, 1], lw=1.2, alpha=0.7,
                         color=_PALETTE.get(name, None))
    # legend once per method
    for name in curves:
        plt.plot([], [], lw=1.6, color=_PALETTE.get(name, None), label=name)
    plt.xlabel("candidate evaluations used")
    plt.ylabel(ylabel)
    plt.grid(alpha=0.3)
    plt.legend()
    if xmax:
        plt.xlim(0, xmax)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
