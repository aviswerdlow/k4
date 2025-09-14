#!/usr/bin/env python3
"""
Golden test suite for Hörenberg K4 exact reproduction.
Validates all discovered conventions and exact matches.
"""

import json
import os
import sys
import unittest

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'layer2_xor'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'layer1_base5'))

from xor5_hoerenberg import xor5_string_hoerenberg, letter_to_code5
from layer2_xor.ioc import calculate_ioc
from layer1_base5.alph25 import ALPH25_DROP_X


class TestHoerenbergExactReproduction(unittest.TestCase):
    """Test suite for exact Hörenberg reproduction."""

    def setUp(self):
        """Load Hörenberg's exact data."""
        data_path = 'layer2_xor/data/hoerenberg_withoutOBKR_extraL.json'
        with open(data_path, 'r') as f:
            self.hoerenberg_data = json.load(f)

    def test_layer2_xor_exact_match(self):
        """Test Layer 2 XOR produces exact P string."""
        c = self.hoerenberg_data['C']
        k = self.hoerenberg_data['K']
        p_expected = self.hoerenberg_data['P']

        p_computed = xor5_string_hoerenberg(c, k)

        self.assertEqual(p_computed, p_expected,
                        "Layer 2 XOR must produce exact P string")

    def test_layer2_ioc_exact_match(self):
        """Test Layer 2 produces exact IoC value."""
        c = self.hoerenberg_data['C']
        k = self.hoerenberg_data['K']
        ioc_expected = self.hoerenberg_data['IoC']

        p_computed = xor5_string_hoerenberg(c, k)
        ioc_computed = calculate_ioc(p_computed)

        self.assertAlmostEqual(ioc_computed, ioc_expected, places=8,
                              msg="IoC must match exactly to 8 decimal places")

    def test_r27_31_passthrough_convention(self):
        """Test R27-31 values are treated as pass-through."""
        # Position 11: C=L, K=W, r=27, should output L
        c_char = 'L'
        k_char = 'W'
        c_code = letter_to_code5(c_char)
        k_code = letter_to_code5(k_char)
        r = c_code ^ k_code

        self.assertEqual(r, 27, "L XOR W should give r=27")

        # Apply XOR - should get pass-through
        from xor5_hoerenberg import xor5_hoerenberg
        result = xor5_hoerenberg(c_char, k_char)
        self.assertEqual(result, c_char,
                        "R=27 should produce pass-through (output C)")

    def test_layer1_ciaw_exact_match(self):
        """Test Layer 1 CIAW example reproduces exactly."""
        cipher = "SHPF"
        key = "OBKR"
        expected = "CIAW"

        result = []
        for c, k in zip(cipher, key):
            c_idx = ALPH25_DROP_X.index(c)
            k_idx = ALPH25_DROP_X.index(k)

            # Base-5 digits
            c_d1, c_d0 = c_idx // 5, c_idx % 5
            k_d1, k_d0 = k_idx // 5, k_idx % 5

            # Addition modulo 5
            r_d1 = (c_d1 + k_d1) % 5
            r_d0 = (c_d0 + k_d0) % 5

            r_idx = r_d1 * 5 + r_d0
            result.append(ALPH25_DROP_X[r_idx])

        result_str = ''.join(result)
        self.assertEqual(result_str, expected,
                        "CIAW must reproduce exactly with drop-X addition")

    def test_keystream_structure(self):
        """Test keystream has expected structure."""
        k = self.hoerenberg_data['K']

        # Check length
        self.assertEqual(len(k), 93, "Keystream must be 93 chars")

        # Check L positions
        l_positions = [i for i, char in enumerate(k) if char == 'L']
        self.assertEqual(len(l_positions), 5, "Should have exactly 5 L's")

        # Check KRYPTOS appears
        self.assertIn("KRYPTOS", k, "Keystream should contain KRYPTOS")

    def test_passthrough_count(self):
        """Test correct number of pass-throughs."""
        c = self.hoerenberg_data['C']
        k = self.hoerenberg_data['K']

        standard_passthrough = 0
        r27_31_passthrough = 0

        for c_char, k_char in zip(c, k):
            c_code = letter_to_code5(c_char)
            k_code = letter_to_code5(k_char)
            r = c_code ^ k_code

            if r == 0:
                standard_passthrough += 1
            elif 27 <= r <= 31:
                r27_31_passthrough += 1

        self.assertEqual(standard_passthrough, 2,
                        "Should have 2 standard pass-throughs (r=0)")
        self.assertEqual(r27_31_passthrough, 17,
                        "Should have 17 R27-31 pass-throughs")


class TestReproductionCompleteness(unittest.TestCase):
    """Test reproduction completeness and documentation."""

    def test_convention_file_exists(self):
        """Test convention documentation exists."""
        convention_file = 'layer2_xor/hoerenberg_convention.json'
        self.assertTrue(os.path.exists(convention_file),
                       "Convention file must exist")

        with open(convention_file, 'r') as f:
            convention = json.load(f)

        self.assertIn('layer2_xor', convention,
                     "Convention must document Layer 2 XOR")

    def test_exact_reproduction_report_exists(self):
        """Test final report exists."""
        report_file = 'EXACT_REPRODUCTION_REPORT.md'
        self.assertTrue(os.path.exists(report_file),
                       "Exact reproduction report must exist")

    def test_all_data_files_present(self):
        """Test all required data files exist."""
        required_files = [
            'layer2_xor/data/hoerenberg_withoutOBKR_extraL.json',
            'layer2_xor/recovered_keystream.json',
            'layer2_xor/xor_verification.json',
            'layer2_xor/keystream_analysis.json'
        ]

        for file_path in required_files:
            self.assertTrue(os.path.exists(file_path),
                           f"Required file {file_path} must exist")


def run_golden_tests():
    """Run all golden tests and report results."""
    print("HÖRENBERG K4 EXACT REPRODUCTION - GOLDEN TEST SUITE")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestHoerenbergExactReproduction))
    suite.addTests(loader.loadTestsFromTestCase(TestReproductionCompleteness))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 70)
    print("GOLDEN TEST RESULTS")
    print("=" * 70)

    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED - EXACT REPRODUCTION CONFIRMED")
        print()
        print("Verified:")
        print("- Layer 2 XOR: Exact P string match")
        print("- Layer 2 IoC: Exact 0.06077606 match")
        print("- R27-31 Convention: Pass-through confirmed")
        print("- Layer 1 CIAW: Exact reproduction")
        print("- Documentation: Complete")
    else:
        print(f"❌ TESTS FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
        for failure in result.failures:
            print(f"\nFailure: {failure[0]}")
            print(failure[1])

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_golden_tests()
    sys.exit(0 if success else 1)