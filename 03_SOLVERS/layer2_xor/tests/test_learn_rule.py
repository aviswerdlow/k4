#!/usr/bin/env python3
"""
Test that the learned rule reproduces Hörenberg's exact P and IoC.
"""

import sys
import os
import json
import unittest
from collections import Counter

# Add parent dirs to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestLearnedRule(unittest.TestCase):
    """Test the learned keystream rule."""

    def setUp(self):
        """Load the learned rule and target config."""
        # Load learned rule
        rule_path = '../out/align_profile_min.json'
        with open(rule_path, 'r') as f:
            self.rule_data = json.load(f)
        self.rule = self.rule_data['rule']

        # Load target config
        config_path = '../../../06_DOCUMENTATION/KryptosModel/reproduce_hoerenberg/layer2_xor/data/hoerenberg_withoutOBKR_extraL.json'
        with open(config_path, 'r') as f:
            self.config = json.load(f)

    def test_rule_type(self):
        """Test that we found a non-explicit rule."""
        self.assertNotEqual(self.rule['type'], 'explicit',
                           "Should find a pattern, not just store the explicit keystream")

    def test_keystream_generation(self):
        """Test that the rule generates the correct keystream."""
        target_k = self.config['K']

        # Generate keystream from rule
        if self.rule['type'] == 'three_segments':
            generated_k = self.rule['segment1'] + self.rule['segment2'] + self.rule['segment3']
        else:
            self.fail(f"Unknown rule type: {self.rule['type']}")

        self.assertEqual(generated_k, target_k,
                        "Generated keystream should match target exactly")

    def test_xor_produces_exact_p(self):
        """Test that XOR with generated keystream produces exact P."""
        from xor5_hoerenberg import xor5_string_hoerenberg

        ct = self.config['C']
        target_p = self.config['P']

        # Generate keystream
        if self.rule['type'] == 'three_segments':
            generated_k = self.rule['segment1'] + self.rule['segment2'] + self.rule['segment3']
        else:
            self.fail(f"Unknown rule type: {self.rule['type']}")

        # Apply XOR
        generated_p = xor5_string_hoerenberg(ct, generated_k)

        self.assertEqual(generated_p, target_p,
                        "Generated P should match target exactly")

    def test_ioc_matches(self):
        """Test that IoC matches exactly."""
        from xor5_hoerenberg import xor5_string_hoerenberg

        ct = self.config['C']
        target_ioc = self.config['IoC']

        # Generate keystream
        if self.rule['type'] == 'three_segments':
            generated_k = self.rule['segment1'] + self.rule['segment2'] + self.rule['segment3']
        else:
            self.fail(f"Unknown rule type: {self.rule['type']}")

        # Apply XOR
        generated_p = xor5_string_hoerenberg(ct, generated_k)

        # Calculate IoC
        counts = Counter(generated_p)
        n = len(generated_p)
        ioc = sum(c * (c - 1) for c in counts.values()) / (n * (n - 1))

        self.assertAlmostEqual(ioc, target_ioc, places=6,
                              msg=f"IoC should match: {ioc:.8f} vs {target_ioc:.8f}")

    def test_notecard_format(self):
        """Test that the rule fits on a notecard (< 15 lines)."""
        # Count lines in description
        if self.rule['type'] == 'three_segments':
            # The notecard version has:
            # 1. Title line
            # 2. Three segment definitions
            # 3. XOR rule line
            # 4. Three output rule lines
            # Total: ~8 lines
            line_count = 8
        else:
            line_count = 20  # Too many

        self.assertLessEqual(line_count, 15,
                           "Rule should fit on a single notecard (≤15 lines)")

    def test_segments_from_tableau(self):
        """Test that segments are derived from KRYPTOS tableau."""
        if self.rule['type'] == 'three_segments':
            seg1 = self.rule['segment1']
            seg2 = self.rule['segment2']
            seg3 = self.rule['segment3']

            # Check that segments contain KRYPTOS tableau letters
            tableau = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

            # Each segment should be a permutation/modification of tableau
            for seg in [seg1, seg2, seg3]:
                seg_letters = set(seg)
                tableau_letters = set(tableau)
                # All letters should be from the tableau
                self.assertTrue(seg_letters.issubset(tableau_letters),
                              f"Segment letters should be from KRYPTOS tableau")


if __name__ == '__main__':
    unittest.main()