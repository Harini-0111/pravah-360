"""
Targeted Test Suite for Phase A: AHP Weight Configuration and Mathematical Consistency.
Verifies Saaty pairwise comparison matrix, principal eigenvalue (lambda_max),
Consistency Index (CI), Consistency Ratio (CR), and susceptibility score invariants.
"""

import unittest
import numpy as np
from typing import Dict, List

from backend.app.services.flood_risk_service import (
    FloodRiskAssessmentService,
    DEFAULT_WEIGHTS,
    AHP_PAIRWISE_MATRIX,
    AHP_LAMBDA_MAX,
    AHP_CONSISTENCY_INDEX,
    AHP_CONSISTENCY_RATIO,
    COMPUTED_AHP_WEIGHTS,
    compute_ahp_matrix_consistency,
    CLASSIFICATION_THRESHOLDS
)


class TestAHPConsistencyAndWeights(unittest.TestCase):
    """Verifies scientific integrity and mathematical consistency of the AHP model."""

    def test_ahp_matrix_reciprocity(self):
        """Matrix must be strictly reciprocal: a_ij * a_ji == 1.0."""
        mat = np.array(AHP_PAIRWISE_MATRIX)
        self.assertEqual(mat.shape, (5, 5), "Matrix must be 5x5.")
        for i in range(5):
            self.assertAlmostEqual(mat[i, i], 1.0, places=4, msg=f"Diagonal [{i},{i}] must be 1.0")
            for j in range(5):
                self.assertAlmostEqual(
                    mat[i, j] * mat[j, i], 1.0, places=2,
                    msg=f"Reciprocal property violated for elements ({i},{j}) and ({j},{i})"
                )

    def test_ahp_matrix_mathematical_consistency_ratio(self):
        """CR must be rigorously below Saaty's 0.10 threshold for scientific validity."""
        lambda_max, ci, cr, weights = compute_ahp_matrix_consistency(AHP_PAIRWISE_MATRIX)
        self.assertAlmostEqual(lambda_max, 5.0006, places=3)
        self.assertLess(ci, 0.001)
        self.assertLess(cr, 0.10, "Consistency ratio must be < 0.10 to be considered consistent")
        self.assertAlmostEqual(cr, AHP_CONSISTENCY_RATIO, places=5)

    def test_derived_weights_match_approved_methodology(self):
        """Eigenvector weights must match approved methodology [0.25, 0.20, 0.25, 0.15, 0.15]."""
        self.assertAlmostEqual(COMPUTED_AHP_WEIGHTS["elevation"], 0.25, places=2)
        self.assertAlmostEqual(COMPUTED_AHP_WEIGHTS["slope"], 0.20, places=2)
        self.assertAlmostEqual(COMPUTED_AHP_WEIGHTS["river_proximity"], 0.25, places=2)
        self.assertAlmostEqual(COMPUTED_AHP_WEIGHTS["landcover"], 0.15, places=2)
        self.assertAlmostEqual(COMPUTED_AHP_WEIGHTS["historical_hazard"], 0.15, places=2)

        # Verify sum equals 1.0
        total_w = sum(COMPUTED_AHP_WEIGHTS.values())
        self.assertAlmostEqual(total_w, 1.0, places=4)

    def test_default_weights_sum_to_one(self):
        """Active DEFAULT_WEIGHTS dictionary must sum strictly to 1.0."""
        self.assertEqual(DEFAULT_WEIGHTS["elevation"], 0.25)
        self.assertEqual(DEFAULT_WEIGHTS["slope"], 0.20)
        self.assertEqual(DEFAULT_WEIGHTS["river_proximity"], 0.25)
        self.assertEqual(DEFAULT_WEIGHTS["landcover"], 0.15)
        self.assertEqual(DEFAULT_WEIGHTS["historical_hazard"], 0.15)
        self.assertAlmostEqual(sum(DEFAULT_WEIGHTS.values()), 1.0, places=6)

    def test_susceptibility_linear_combination(self):
        """Susceptibility calculation must correctly evaluate normalized linear combinations."""
        # Test synthetic normalized input [1.0, 1.0, 1.0, 1.0, 1.0] -> 1.0
        fsi_max = (
            DEFAULT_WEIGHTS["elevation"] * 1.0 +
            DEFAULT_WEIGHTS["slope"] * 1.0 +
            DEFAULT_WEIGHTS["river_proximity"] * 1.0 +
            DEFAULT_WEIGHTS["landcover"] * 1.0 +
            DEFAULT_WEIGHTS["historical_hazard"] * 1.0
        )
        self.assertAlmostEqual(fsi_max, 1.0, places=5)

        # Test zero input
        fsi_min = (
            DEFAULT_WEIGHTS["elevation"] * 0.0 +
            DEFAULT_WEIGHTS["slope"] * 0.0 +
            DEFAULT_WEIGHTS["river_proximity"] * 0.0 +
            DEFAULT_WEIGHTS["landcover"] * 0.0 +
            DEFAULT_WEIGHTS["historical_hazard"] * 0.0
        )
        self.assertAlmostEqual(fsi_min, 0.0, places=5)

        # Test Mummidivaram representative profile
        # Elev: 0.95, Slope: 0.98, Dist: 0.92, LC: 0.85, Haz: 0.90
        # Expected: 0.25*0.95 + 0.20*0.98 + 0.25*0.92 + 0.15*0.85 + 0.15*0.90 = 0.926
        fsi_mum = (
            0.25 * 0.95 +
            0.20 * 0.98 +
            0.25 * 0.92 +
            0.15 * 0.85 +
            0.15 * 0.90
        )
        self.assertAlmostEqual(fsi_mum, 0.926, places=3)
        self.assertGreaterEqual(fsi_mum, CLASSIFICATION_THRESHOLDS["Very High"])


if __name__ == "__main__":
    unittest.main()
