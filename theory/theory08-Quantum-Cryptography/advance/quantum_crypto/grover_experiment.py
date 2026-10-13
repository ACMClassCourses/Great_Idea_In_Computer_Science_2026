"""Exact 2–4 qubit Grover simulation with seeded finite-shot observations."""

from __future__ import annotations

import argparse
import math
import random
from collections.abc import Iterable


def uniform_state(qubits: int) -> list[complex]:
    if not 1 <= qubits <= 4:
        raise ValueError("this teaching simulator supports 1 through 4 qubits")
    return [1 / math.sqrt(1 << qubits)] * (1 << qubits)


def validate_targets(size: int, targets: Iterable[int]) -> tuple[int, ...]:
    result = tuple(sorted(set(targets)))
    if not result or any(target < 0 or target >= size for target in result):
        raise ValueError("targets must be distinct basis-state indices in [0, 2^n)")
    return result


def phase_oracle(state: list[complex], targets: Iterable[int]) -> None:
    """Negate amplitudes of the marked basis states."""
    for target in targets:
        state[target] = -state[target]


def diffusion(state: list[complex]) -> None:
    """Reflect amplitudes about their mean: a_i -> 2*mean(a) - a_i."""
    mean = sum(state) / len(state)
    for index, amplitude in enumerate(state):
        state[index] = 2 * mean - amplitude


def success_probability(state: list[complex], targets: Iterable[int]) -> float:
    return sum(abs(state[target]) ** 2 for target in targets)


def theoretical_success(qubits: int, marked: int, iterations: int) -> float:
    theta = math.asin(math.sqrt(marked / (1 << qubits)))
    return math.sin((2 * iterations + 1) * theta) ** 2


def sample_success(state: list[complex], targets: set[int], shots: int, seed: int) -> float:
    if shots <= 0:
        raise ValueError("shots must be positive")
    weights = [abs(value) ** 2 for value in state]
    rng = random.Random(seed)
    successes = 0
    for _ in range(shots):
        draw, cumulative = rng.random(), 0.0
        for index, weight in enumerate(weights):
            cumulative += weight
            if draw <= cumulative or index == len(weights) - 1:
                successes += index in targets
                break
    return successes / shots


def run_curve(qubits: int, targets: Iterable[int], max_iterations: int, shots: int, seed: int) -> list[dict[str, float | int]]:
    size = 1 << qubits
    marked = validate_targets(size, targets)
    if max_iterations < 0:
        raise ValueError("max_iterations must be non-negative")
    state = uniform_state(qubits)
    rows: list[dict[str, float | int]] = []
    for iteration in range(max_iterations + 1):
        rows.append({
            "qubits": qubits,
            "marked": len(marked),
            "iteration": iteration,
            "simulated_success": success_probability(state, marked),
            "theoretical_success": theoretical_success(qubits, len(marked), iteration),
            "sampled_success": sample_success(state, set(marked), shots, seed + iteration),
        })
        phase_oracle(state, marked)
        diffusion(state)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qubits", type=int, nargs="+", default=[2, 3, 4])
    parser.add_argument("--target", type=int, nargs="+", default=[0])
    parser.add_argument("--max-iterations", type=int, default=5)
    parser.add_argument("--shots", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260929)
    args = parser.parse_args()

    print("qubits,marked,iteration,simulated_success,theoretical_success,sampled_success")
    for qubits in args.qubits:
        for row in run_curve(qubits, args.target, args.max_iterations, args.shots, args.seed):
            print(
                f"{row['qubits']},{row['marked']},{row['iteration']},"
                f"{row['simulated_success']:.12f},{row['theoretical_success']:.12f},"
                f"{row['sampled_success']:.12f}"
            )


if __name__ == "__main__":
    main()
