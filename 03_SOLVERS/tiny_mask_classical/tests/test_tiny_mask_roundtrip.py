#!/usr/bin/env python3
"""
Test tiny mask + classical round-trip and null hypothesis gates.
"""

import sys
import os
import json
import unittest
from collections import Counter

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runner import (
    Interleave2Mask, VigenereCipher, BeaufortCipher,
    calculate_ioc, calculate_english_score
)


class TestTinyMaskRoundtrip(unittest.TestCase):
    """Test tiny mask + classical synthesis."""

    def setUp(self):
        """Load K4 ciphertext."""
        ct_path = '../../../02_DATA/ciphertext_97.txt'
        with open(ct_path, 'r') as f:
            self.k4_ct = f.read().strip().upper()

        # Load search summary if exists
        summary_path = '../out/search_summary.json'
        if os.path.exists(summary_path):
            with open(summary_path, 'r') as f:
                self.summary = json.load(f)
        else:
            self.summary = None

    def test_round_trip_interleave2_vigenere(self):
        """Test that interleave2 + Vigenere round-trips."""
        mask = Interleave2Mask()
        cipher = VigenereCipher('KRYPTOS')

        # Decrypt
        intermediate = cipher.decrypt(self.k4_ct)
        unmasked, mask_info = mask.apply(intermediate)
        plaintext = mask.invert(intermediate, mask_info)

        # Re-encrypt
        remasked, _ = mask.apply(plaintext)
        reconstructed = cipher.encrypt(remasked)

        self.assertEqual(reconstructed, self.k4_ct,
                        "Should round-trip to original ciphertext")

    def test_round_trip_reverse_beaufort(self):
        """Test that reverse + Beaufort round-trips."""
        from runner import ReverseMask

        mask = ReverseMask()
        cipher = BeaufortCipher('AZIMUTH')

        # Decrypt (mask then cipher order)
        intermediate = cipher.decrypt(self.k4_ct)
        unmasked, mask_info = mask.apply(intermediate)
        plaintext = mask.invert(intermediate, mask_info)

        # Re-encrypt
        remasked, _ = mask.apply(plaintext)
        reconstructed = cipher.encrypt(remasked)

        self.assertEqual(reconstructed, self.k4_ct,
                        "Should round-trip to original ciphertext")

    def test_null_hypothesis_thresholds(self):
        """Test null hypothesis thresholds."""
        # Random text should have IoC around 0.0385
        random_text = "XQJKVBZWPTYUDFGHASLCMNROEIXQJKV" * 3
        ioc_random = calculate_ioc(random_text)
        self.assertLess(ioc_random, 0.045, "Random IoC should be low")
        self.assertGreater(ioc_random, 0.030, "Random IoC should be in expected range")

        # Text with repeated patterns should have higher IoC
        patterned_text = "THETHETHETHETHETHETHETHETHETHE" * 3
        ioc_patterned = calculate_ioc(patterned_text)
        self.assertGreater(ioc_patterned, 0.100, "Patterned text IoC should be much higher")

    def test_search_completeness(self):
        """Test that search covered expected space."""
        self.assertIsNotNone(self.summary, "Should have search summary")

        expected_combinations = 5 * 5 * 2 * 2  # masks * keys * ciphers * orders
        self.assertEqual(self.summary['search_space']['total_combinations'],
                        expected_combinations,
                        "Should test all combinations")

        self.assertGreater(self.summary['round_trip_ok'], 0,
                          "Should have some round-trip successes")

    def test_no_solutions_beat_nulls(self):
        """Test that no solutions beat null hypotheses (as found)."""
        self.assertIsNotNone(self.summary, "Should have search summary")
        self.assertEqual(self.summary['beat_nulls'], 0,
                        "Confirmed: no candidates beat null hypotheses")

    def test_best_candidate_properties(self):
        """Test properties of best candidates."""
        # Load candidates if available
        import glob
        candidate_files = glob.glob('../out/candidates_*.jsonl')

        if candidate_files:
            best_ioc = 0
            best_english = 0

            with open(candidate_files[0], 'r') as f:
                for line in f:
                    candidate = json.loads(line)
                    if candidate['round_trip']:
                        best_ioc = max(best_ioc, candidate['ioc'])
                        best_english = max(best_english, candidate['english_score'])

            # Best candidates should at least be non-random
            self.assertGreater(best_ioc, 0.030, "Best IoC should be non-random")
            self.assertGreater(best_english, 0.5, "Best English score should be non-zero")


if __name__ == '__main__':
    unittest.main()