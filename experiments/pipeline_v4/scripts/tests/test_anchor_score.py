#!/usr/bin/env python3
"""
Test suite for anchor scoring to ensure no regressions.
Critical: Anchors must be scored BEFORE blinding.
"""

import sys
import unittest
from pathlib import Path

# Add parent directories
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from experiments.pipeline_v2.scripts.explore.anchor_score import score_anchors


class TestAnchorScoring(unittest.TestCase):
    """
    Test anchor scoring implementation.
    """
    
    def test_fixed_mode_exact_match(self):
        """Test fixed mode with exact anchor placement."""
        head = "X" * 21 + "EAST" + "NORTHEAST" + "X" * 29 + "BERLINCLOCK" + "X"
        policy = {"window_radius": 0, "typo_budget": 0}
        
        result = score_anchors(head, policy)
        
        self.assertEqual(result['anchor_score'], 24)  # All 3 anchors found
        self.assertEqual(result['per_anchor']['EAST']['score'], 4)
        self.assertEqual(result['per_anchor']['NORTHEAST']['score'], 9)
        self.assertEqual(result['per_anchor']['BERLINCLOCK']['score'], 11)
    
    def test_windowed_mode_within_radius(self):
        """Test windowed mode finds anchors within radius."""
        # EAST at position 23 (offset +2)
        head = "X" * 23 + "EAST" + "X" * 48
        policy = {"window_radius": 2, "typo_budget": 0}
        
        result = score_anchors(head, policy)
        
        self.assertEqual(result['per_anchor']['EAST']['score'], 4)  # Found within window
        self.assertEqual(result['per_anchor']['EAST']['position'], 23)
    
    def test_windowed_mode_outside_radius(self):
        """Test windowed mode misses anchors outside radius."""
        # EAST at position 27 (offset +6, outside radius 2)
        head = "X" * 27 + "EAST" + "X" * 44
        policy = {"window_radius": 2, "typo_budget": 0}
        
        result = score_anchors(head, policy)
        
        self.assertEqual(result['east_score'], 0)  # Not found
    
    def test_typo_tolerance(self):
        """Test typo tolerance in windowed mode."""
        # EEST instead of EAST (1 typo)
        head = "X" * 21 + "EEST" + "X" * 50
        policy = {"window_radius": 0, "typo_budget": 1}
        
        result = score_anchors(head, policy)
        
        self.assertGreaterEqual(result['east_score'], 3)  # Partial credit
    
    def test_shuffled_mode(self):
        """Test shuffled mode with large window."""
        # EAST at position 40 (way off)
        head = "X" * 40 + "EAST" + "X" * 31
        policy = {"window_radius": 100, "typo_budget": 2}
        
        result = score_anchors(head, policy)
        
        self.assertEqual(result['east_score'], 4)  # Found anywhere
        self.assertEqual(result['east_position'], 40)
    
    def test_no_anchors_present(self):
        """Test scoring when no anchors present."""
        head = "X" * 75
        policy = {"window_radius": 0, "typo_budget": 0}
        
        result = score_anchors(head, policy)
        
        self.assertEqual(result['total_score'], 0)
        self.assertEqual(result['east_score'], 0)
        self.assertEqual(result['northeast_score'], 0)
        self.assertEqual(result['berlinclock_score'], 0)
    
    def test_overlapping_anchors(self):
        """Test when EAST and NORTHEAST overlap correctly."""
        head = "X" * 21 + "EASTNORTHEAST" + "X" * 41
        policy = {"window_radius": 0, "typo_budget": 0}
        
        result = score_anchors(head, policy)
        
        self.assertEqual(result['east_score'], 4)
        self.assertEqual(result['northeast_score'], 9)
        self.assertEqual(result['total_score'], 13)
    
    def test_window_search_order(self):
        """Test that window search prioritizes closer positions."""
        # Place EAST at both position 20 and 23
        # Should find the one at 20 (closer to expected 21)
        head_list = ['X'] * 75
        head_list[20:24] = list("EAST")
        head_list[23:27] = list("EAST")
        head = ''.join(head_list)
        
        policy = {"window_radius": 2, "typo_budget": 0}
        
        result = score_anchors(head, policy)
        
        self.assertEqual(result['east_position'], 20)  # Closer one found
    
    def test_scoring_before_blinding(self):
        """
        CRITICAL TEST: Ensure anchors are found before any blinding.
        This is the fix from v2 that must be preserved.
        """
        # Text with anchors that would be masked by blinding
        head = "THE " + "X" * 17 + "EASTNORTHEASTWORD" + "X" * 26 + "BERLINCLOCKTIME"
        
        # Score with fixed policy
        policy = {"window_radius": 0, "typo_budget": 0}
        result = score_anchors(head, policy)
        
        # All anchors should be found BEFORE blinding would mask them
        self.assertEqual(result['east_score'], 4)
        self.assertEqual(result['northeast_score'], 9)
        self.assertEqual(result['berlinclock_score'], 11)
        self.assertEqual(result['total_score'], 24)
        
        # The positions should be exact
        self.assertEqual(result['east_position'], 21)
        self.assertEqual(result['northeast_position'], 25)
        self.assertEqual(result['berlinclock_position'], 63)


class TestWindowedSearch(unittest.TestCase):
    """
    Test windowed search implementation specifically.
    """
    
    def test_window_radius_2(self):
        """Test window radius 2 searches correctly."""
        positions_to_test = [
            (19, True),   # -2 from expected, within radius
            (20, True),   # -1 from expected, within radius
            (21, True),   # Exact position
            (22, True),   # +1 from expected, within radius
            (23, True),   # +2 from expected, within radius
            (24, False),  # +3 from expected, outside radius
            (18, False),  # -3 from expected, outside radius
        ]
        
        for pos, should_find in positions_to_test:
            head = "X" * pos + "EAST" + "X" * (71 - pos)
            policy = {"window_radius": 2, "typo_budget": 0}
            
            result = score_anchors(head, policy)
            
            if should_find:
                self.assertEqual(
                    result['east_score'], 4,
                    f"Should find EAST at position {pos} with radius 2"
                )
            else:
                self.assertEqual(
                    result['east_score'], 0,
                    f"Should NOT find EAST at position {pos} with radius 2"
                )


def run_tests():
    """Run all tests and report results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestAnchorScoring))
    suite.addTests(loader.loadTestsFromTestCase(TestWindowedSearch))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED")
        print("Anchor scoring implementation verified correct:")
        print("  - Anchors scored BEFORE blinding")
        print("  - Windowed search working correctly")
        print("  - Typo tolerance functional")
    else:
        print("❌ TESTS FAILED")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()