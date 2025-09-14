#!/usr/bin/env python3
"""
Test mini-examples for Layer-1 base-5.
Expects CIAW exact match and certificates for CIAX/CULDWW.
"""

import sys
import os
import json
import unittest

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMiniExamples(unittest.TestCase):
    """Test Layer-1 mini-examples."""

    def setUp(self):
        """Load results and certificates."""
        # Check for no-solution certificate
        cert_path = '../out/no_solution_certificate_final.json'
        if os.path.exists(cert_path):
            with open(cert_path, 'r') as f:
                self.certificate = json.load(f)
        else:
            self.certificate = None

        # Check for exact matches
        # Find the most recent exact matches file
        import glob
        exact_files = glob.glob('../out/exact_matches_*.json')
        if exact_files:
            latest_exact = sorted(exact_files)[-1]
            with open(latest_exact, 'r') as f:
                self.exact_matches = json.load(f)
        else:
            self.exact_matches = None

    def test_ciaw_exact(self):
        """Test that CIAW has exact matches."""
        self.assertIsNotNone(self.exact_matches, "Should have exact matches file")
        self.assertIn('CIAW', self.exact_matches, "Should have CIAW results")
        self.assertGreater(len(self.exact_matches['CIAW']), 0,
                           "CIAW should have at least one exact match")

        # Verify the match details
        for match in self.exact_matches['CIAW']:
            self.assertEqual(match['result'], 'CIAW', "Result should be CIAW")
            self.assertEqual(match['p'], 'SHPF', "P segment should be SHPF")
            self.assertEqual(match['k'], 'OBKR', "K segment should be OBKR")

    def test_ciax_no_solution(self):
        """Test that CIAX has no solution certificate."""
        self.assertIsNotNone(self.certificate, "Should have no-solution certificate")
        self.assertEqual(self.certificate['certification']['CIAX'], 'NO SOLUTION FOUND',
                        "CIAX should be certified as having no solution")
        self.assertEqual(self.certificate['results']['CIAX']['exact_matches'], 0,
                        "CIAX should have 0 exact matches")

    def test_culdww_no_solution(self):
        """Test that CULDWW has no solution certificate."""
        self.assertIsNotNone(self.certificate, "Should have no-solution certificate")
        self.assertEqual(self.certificate['certification']['CULDWW'], 'NO SOLUTION FOUND',
                        "CULDWW should be certified as having no solution")
        self.assertEqual(self.certificate['results']['CULDWW']['exact_matches'], 0,
                        "CULDWW should have 0 exact matches")

    def test_search_parameters(self):
        """Test that search was comprehensive."""
        self.assertIsNotNone(self.certificate, "Should have certificate")
        params = self.certificate['search_parameters']

        # Check expanded search parameters
        self.assertEqual(params['total_conventions'], 192,
                        "Should test 192 conventions (64 base + 128 expanded)")
        self.assertEqual(params['index_window'], '±10',
                        "Should use ±10 index window")
        self.assertIn('mixed_operation', params['expanded_toggles'],
                     "Should include mixed_operation toggle")
        self.assertIn('swap_on_passthrough', params['expanded_toggles'],
                     "Should include swap_on_passthrough toggle")

    def test_ciaw_convention(self):
        """Test that CIAW uses drop-X alphabet with addition."""
        self.assertIsNotNone(self.exact_matches, "Should have exact matches")
        self.assertGreater(len(self.exact_matches['CIAW']), 0, "Should have CIAW matches")

        # Check that at least one match uses the expected convention
        found_expected = False
        for match in self.exact_matches['CIAW']:
            conv = match['convention']
            if (conv['alphabet'] == 'drop-X' and
                conv['operation'] == 'add' and
                match.get('p_position', 0) == 0):
                found_expected = True
                break

        self.assertTrue(found_expected,
                       "Should find CIAW with drop-X alphabet, addition, at position 0")


if __name__ == '__main__':
    unittest.main()