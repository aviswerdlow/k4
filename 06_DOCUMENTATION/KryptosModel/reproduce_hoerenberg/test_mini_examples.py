#!/usr/bin/env python3
"""
Golden tests for Layer-1 mini-examples.
Enforces exact CIAW reproduction and validates no-solution certificate for CIAX/CULDWW.
"""

import unittest
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'layer1_base5'))
from alph25 import ALPH25_DROP_X


class TestMiniExamples(unittest.TestCase):
    """Test Layer-1 mini-examples for exact reproduction or certified infeasibility."""

    def test_ciaw_exact_reproduction(self):
        """Test that CIAW is reproduced exactly with discovered convention."""
        # Known working convention: drop-X, addition, standard mapping
        cipher = "SHPF"
        key = "OBKR"
        expected = "CIAW"

        result = []
        for c, k in zip(cipher, key):
            self.assertIn(c, ALPH25_DROP_X, f"{c} must be in drop-X alphabet")
            self.assertIn(k, ALPH25_DROP_X, f"{k} must be in drop-X alphabet")

            c_idx = ALPH25_DROP_X.index(c)
            k_idx = ALPH25_DROP_X.index(k)

            # Standard row-major, d1=row, d0=col
            c_d1, c_d0 = c_idx // 5, c_idx % 5
            k_d1, k_d0 = k_idx // 5, k_idx % 5

            # Addition modulo 5
            r_d1 = (c_d1 + k_d1) % 5
            r_d0 = (c_d0 + k_d0) % 5

            r_idx = r_d1 * 5 + r_d0
            self.assertLess(r_idx, 25, "Result index must be valid")

            result.append(ALPH25_DROP_X[r_idx])

        result_str = ''.join(result)
        self.assertEqual(result_str, expected,
                        f"CIAW must reproduce exactly: {cipher} + {key} = {expected}")

    def test_ciax_infeasibility_certificate(self):
        """Test that CIAX has a valid no-solution certificate."""
        # Check for no-solution certificate
        cert_files = [
            'layer1_base5/no_solution_certificate.json',
            'layer1_base5/no_solution_certificate_final.json'
        ]

        cert_found = False
        for cert_file in cert_files:
            if os.path.exists(cert_file):
                cert_found = True
                with open(cert_file, 'r') as f:
                    certificate = json.load(f)

                # Validate certificate structure
                self.assertIn('search_parameters', certificate,
                             "Certificate must document search parameters")
                self.assertIn('results', certificate,
                             "Certificate must document results")

                # Verify CIAX was not found
                if 'results' in certificate:
                    self.assertIn('CIAX', certificate['results'])
                    self.assertEqual(certificate['results']['CIAX'], 'NOT_FOUND',
                                   "CIAX must be documented as not found")

                # Verify comprehensive search
                if 'search_parameters' in certificate:
                    params = certificate['search_parameters']
                    self.assertGreaterEqual(params.get('total_conventions', 0), 64,
                                          "Must test at least 64 base conventions")

                break

        self.assertTrue(cert_found,
                       "No-solution certificate must exist for CIAX")

    def test_culdww_infeasibility_certificate(self):
        """Test that CULDWW has a valid no-solution certificate."""
        # Check for no-solution certificate
        cert_files = [
            'layer1_base5/no_solution_certificate.json',
            'layer1_base5/no_solution_certificate_final.json'
        ]

        cert_found = False
        for cert_file in cert_files:
            if os.path.exists(cert_file):
                cert_found = True
                with open(cert_file, 'r') as f:
                    certificate = json.load(f)

                # Verify CULDWW was not found
                if 'results' in certificate:
                    self.assertIn('CULDWW', certificate['results'])
                    self.assertEqual(certificate['results']['CULDWW'], 'NOT_FOUND',
                                   "CULDWW must be documented as not found")

                break

        self.assertTrue(cert_found,
                       "No-solution certificate must exist for CULDWW")

    def test_grid_search_completeness(self):
        """Test that grid search was comprehensive."""
        # Check that grid search results exist
        import glob
        grid_files = glob.glob('layer1_base5/grid_search_exact_*.json')

        self.assertGreater(len(grid_files), 0,
                          "Grid search results must exist")

        # Load most recent grid search
        if grid_files:
            latest_file = sorted(grid_files)[-1]
            with open(latest_file, 'r') as f:
                grid_results = json.load(f)

            # Verify CIAW was found
            self.assertIn('CIAW', grid_results)
            self.assertGreater(len(grid_results['CIAW']), 0,
                              "CIAW must be found in grid search")

            # Verify search was run for all targets
            self.assertIn('CIAX', grid_results)
            self.assertIn('CULDWW', grid_results)


class TestConventionDocumentation(unittest.TestCase):
    """Test that conventions are properly documented."""

    def test_ciaw_convention_documented(self):
        """Test CIAW convention is documented."""
        # Check multiple possible locations
        doc_files = [
            'NOTES_ON_MAPPING.md',
            'EXACT_REPRODUCTION_REPORT.md',
            'layer1_base5/CIAW_CONVENTION.md'
        ]

        doc_found = False
        for doc_file in doc_files:
            if os.path.exists(doc_file):
                with open(doc_file, 'r') as f:
                    content = f.read()
                    if 'CIAW' in content and 'drop-X' in content:
                        doc_found = True
                        break

        self.assertTrue(doc_found,
                       "CIAW convention must be documented")

    def test_infeasibility_documented(self):
        """Test CIAX/CULDWW infeasibility is documented."""
        report_file = 'EXACT_REPRODUCTION_REPORT.md'

        self.assertTrue(os.path.exists(report_file),
                       "Exact reproduction report must exist")

        with open(report_file, 'r') as f:
            content = f.read()

        # Check that infeasibility is mentioned
        self.assertIn('CIAX', content, "CIAX must be mentioned in report")
        self.assertIn('CULDWW', content, "CULDWW must be mentioned in report")

        # Check for idealized/infeasible language
        idealized_mentioned = ('idealized' in content.lower() or
                              'cannot reproduce' in content.lower() or
                              'not found' in content.lower())

        self.assertTrue(idealized_mentioned,
                       "Report must document that CIAX/CULDWW cannot be reproduced")


def run_mini_example_tests():
    """Run all mini-example tests."""
    print("LAYER-1 MINI-EXAMPLES - GOLDEN TEST SUITE")
    print("=" * 70)
    print()

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestMiniExamples))
    suite.addTests(loader.loadTestsFromTestCase(TestConventionDocumentation))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print("MINI-EXAMPLE TEST RESULTS")
    print("=" * 70)

    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED")
        print()
        print("Verified:")
        print("- CIAW: Exact reproduction confirmed")
        print("- CIAX: No-solution certificate validated")
        print("- CULDWW: No-solution certificate validated")
        print("- Documentation: Complete")
    else:
        print(f"❌ TESTS FAILED: {len(result.failures)} failures, {len(result.errors)} errors")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_mini_example_tests()
    sys.exit(0 if success else 1)