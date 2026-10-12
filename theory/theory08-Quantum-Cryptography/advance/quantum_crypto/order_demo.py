"""Classical order-finding demonstration for N=15, a=2; not a Shor implementation."""

from __future__ import annotations

import argparse
import math


def multiplicative_order(base: int, modulus: int) -> int:
    """Find the least r > 0 satisfying base**r == 1 (mod modulus) by a classical loop."""
    if modulus <= 1:
        raise ValueError("modulus must exceed 1")
    base %= modulus
    if math.gcd(base, modulus) != 1:
        raise ValueError("base and modulus must be coprime")
    value = 1
    for order in range(1, modulus + 1):
        value = (value * base) % modulus
        if value == 1:
            return order
    raise RuntimeError("order was not found")


def factors_from_order(base: int, modulus: int, order: int) -> tuple[int, int] | None:
    """Apply the classical post-processing condition used after Shor's order estimate."""
    if order <= 0 or order % 2:
        return None
    half_power = pow(base, order // 2, modulus)
    if half_power == modulus - 1:
        return None
    left = math.gcd(half_power - 1, modulus)
    right = math.gcd(half_power + 1, modulus)
    if 1 < left < modulus and 1 < right < modulus:
        return tuple(sorted((left, right)))
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modulus", type=int, default=15)
    parser.add_argument("--base", type=int, default=2)
    args = parser.parse_args()

    order = multiplicative_order(args.base, args.modulus)
    half_power = pow(args.base, order // 2, args.modulus) if order % 2 == 0 else None
    factors = factors_from_order(args.base, args.modulus, order)
    print(f"a={args.base}, N={args.modulus}")
    print(f"classical order r={order}: {args.base}^{order} mod {args.modulus} = 1")
    if half_power is not None:
        print(f"a^(r/2) mod N = {half_power}")
        print(f"gcd(a^(r/2)-1, N) = {math.gcd(half_power - 1, args.modulus)}")
        print(f"gcd(a^(r/2)+1, N) = {math.gcd(half_power + 1, args.modulus)}")
    if factors:
        print(f"non-trivial factors: {factors[0]} * {factors[1]} = {args.modulus}")
    else:
        print("This base/order does not yield non-trivial factors; choose another base and retry.")


if __name__ == "__main__":
    main()
