import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from quantum_crypto.basic_circuits import evolve, probabilities, sample_counts
from quantum_crypto.grover_experiment import run_curve
from quantum_crypto.order_demo import factors_from_order, multiplicative_order


class BasicCircuitTests(unittest.TestCase):
    def test_hzh_turns_phase_into_measurement_difference(self):
        p0, p1 = probabilities(evolve(("H", "Z", "H")))
        self.assertAlmostEqual(p0, 0.0, places=12)
        self.assertAlmostEqual(p1, 1.0, places=12)

    def test_seeded_sampling_is_reproducible(self):
        state = evolve(("H",))
        self.assertEqual(sample_counts(state, 1000, 20260929), sample_counts(state, 1000, 20260929))


class GroverTests(unittest.TestCase):
    def test_state_vector_matches_theory(self):
        for row in run_curve(3, [0], max_iterations=4, shots=20, seed=7):
            self.assertAlmostEqual(row["simulated_success"], row["theoretical_success"], places=12)

    def test_too_many_iterations_reduce_success_probability(self):
        rows = run_curve(3, [0], max_iterations=3, shots=20, seed=7)
        self.assertGreater(rows[2]["simulated_success"], rows[3]["simulated_success"])


class OrderFindingTests(unittest.TestCase):
    def test_n15_a2(self):
        order = multiplicative_order(2, 15)
        self.assertEqual(order, 4)
        self.assertEqual(factors_from_order(2, 15, order), (3, 5))

    def test_non_coprime_base_is_rejected(self):
        with self.assertRaises(ValueError):
            multiplicative_order(3, 15)


if __name__ == "__main__":
    unittest.main()
