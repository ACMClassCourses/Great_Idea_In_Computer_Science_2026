"""Single-qubit Basic experiments: state evolution and seeded sampling."""

from __future__ import annotations

import argparse
import math
import random
from collections.abc import Iterable

State = tuple[complex, complex]
INV_SQRT2 = 1 / math.sqrt(2)


def apply_gate(state: State, gate: str) -> State:
    """Apply one H/X/Z gate; the first component is the |0> amplitude."""
    a, b = state
    if gate == "H":
        return ((a + b) * INV_SQRT2, (a - b) * INV_SQRT2)
    if gate == "X":
        return b, a
    if gate == "Z":
        return a, -b
    raise ValueError(f"unsupported gate: {gate}")


def evolve(gates: Iterable[str]) -> State:
    state: State = (1 + 0j, 0j)
    for gate in gates:
        state = apply_gate(state, gate)
    return state


def probabilities(state: State) -> tuple[float, float]:
    return abs(state[0]) ** 2, abs(state[1]) ** 2


def sample_counts(state: State, shots: int, seed: int) -> tuple[int, int]:
    if shots <= 0:
        raise ValueError("shots must be positive")
    p0, _ = probabilities(state)
    rng = random.Random(seed)
    zeros = sum(rng.random() < p0 for _ in range(shots))
    return zeros, shots - zeros


EXPERIMENTS: dict[str, tuple[str, ...]] = {
    "I": (),
    "H": ("H",),
    "HH": ("H", "H"),
    "HZH": ("H", "Z", "H"),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shots", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260929)
    args = parser.parse_args()

    print("circuit,p0,p1,count_0,count_1")
    for offset, (name, gates) in enumerate(EXPERIMENTS.items()):
        state = evolve(gates)
        p0, p1 = probabilities(state)
        c0, c1 = sample_counts(state, args.shots, args.seed + offset)
        print(f"{name},{p0:.12f},{p1:.12f},{c0},{c1}")


if __name__ == "__main__":
    main()
