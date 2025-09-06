#!/usr/bin/env python3
"""
Unit tests for anchor alignment scoring.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from experiments.pipeline_v2.scripts.explore.anchor_score import (
    score_anchors, hamming_distance, combine_scores
)


def test_fixed_exact_hit():
    """Test fixed mode with exact anchor match."""
    # Build head with anchors at correct positions
    head = "X" * 21  # 0-20
    head += "EAST"  # 21-24
    head += "NORTHEAST"  # 25-33
    head += "X" * 29  # 34-62 
    head += "BERLINCLOCK"  # 63-73
    head += "X"  # 74
    
    policy = {
        "anchor_scoring": {
            "mode": "fixed",
            "anchors": [
                {"token": "EAST", "start": 21},
                {"token": "NORTHEAST", "start": 25},
                {"token": "BERLINCLOCK", "start": 63}
            ],
            "flexibility": {"r": 0, "typo_budget": 0},
            "weights": {
                "lambda_pos": 1.0,
                "lambda_typo": 1.0
            }
        }
    }
    
    result = score_anchors(head, policy)
    
    assert result["anchor_score"] == 1.0, f"Expected 1.0, got {result['anchor_score']}"
    for anchor in result["per_anchor"]:
        assert anchor["hit"] == True, f"{anchor['token']} should hit"
        assert anchor["offset"] == 0, f"{anchor['token']} offset should be 0"
        assert anchor["typos"] == 0, f"{anchor['token']} typos should be 0"
        assert anchor["contrib"] == 1.0, f"{anchor['token']} contrib should be 1.0"
    
    print("✓ Fixed exact hit test passed")


def test_windowed_offset():
    """Test windowed mode with offset anchor."""
    # EAST at position 22 instead of 21
    head = "X" * 22  # 0-21
    head += "EAST"  # 22-25 (offset by 1)
    head += "NORTHEAST"  # 26-34
    head += "X" * 28  # 35-62
    head += "BERLINCLOCK"  # 63-73
    head += "X"  # 74
    
    policy = {
        "anchor_scoring": {
            "mode": "windowed",
            "anchors": [
                {"token": "EAST", "start": 21},
                {"token": "NORTHEAST", "start": 25},
                {"token": "BERLINCLOCK", "start": 63}
            ],
            "flexibility": {"r": 2, "typo_budget": 0},
            "weights": {
                "lambda_pos": 1.0,
                "lambda_typo": 1.0
            }
        }
    }
    
    result = score_anchors(head, policy)
    
    # EAST should be found at offset 1
    east_result = result["per_anchor"][0]
    assert east_result["hit"] == True, "EAST should hit within window"
    assert east_result["found"] == 22, f"EAST should be found at 22, got {east_result['found']}"
    assert east_result["offset"] == 1, f"EAST offset should be 1, got {east_result['offset']}"
    assert east_result["typos"] == 0, "EAST should have no typos"
    assert east_result["contrib"] < 1.0, f"EAST contrib should be < 1.0, got {east_result['contrib']}"
    assert east_result["contrib"] == 0.5, f"EAST contrib should be 0.5 (1 - 1*1/2), got {east_result['contrib']}"
    
    print("✓ Windowed offset test passed")


def test_windowed_typo():
    """Test windowed mode with typo."""
    # EAZT instead of EAST (1 typo)
    head = "X" * 21 + "EAZT" + "NORTHEAST" + "X" * 29 + "BERLINCLOCK" + "X"
    
    policy = {
        "anchor_scoring": {
            "mode": "windowed",
            "anchors": [
                {"token": "EAST", "start": 21}
            ],
            "flexibility": {"r": 0, "typo_budget": 1},
            "weights": {
                "lambda_pos": 1.0,
                "lambda_typo": 1.0
            }
        }
    }
    
    result = score_anchors(head, policy)
    
    east_result = result["per_anchor"][0]
    assert east_result["hit"] == True, "EAST should hit with 1 typo allowed"
    assert east_result["found"] == 21, f"EAST should be found at 21"
    assert east_result["offset"] == 0, "EAST offset should be 0"
    assert east_result["typos"] == 1, f"EAST should have 1 typo, got {east_result['typos']}"
    assert east_result["contrib"] < 1.0, f"EAST contrib should be < 1.0 due to typo"
    
    print("✓ Windowed typo test passed")


def test_miss():
    """Test anchor miss."""
    # No EAST in the head
    head = "X" * 21 + "XXXX" + "NORTHEAST" + "X" * 29 + "BERLINCLOCK" + "X"
    
    policy = {
        "anchor_scoring": {
            "mode": "fixed",
            "anchors": [
                {"token": "EAST", "start": 21}
            ],
            "flexibility": {"r": 0, "typo_budget": 0},
            "weights": {
                "lambda_pos": 1.0,
                "lambda_typo": 1.0
            }
        }
    }
    
    result = score_anchors(head, policy)
    
    east_result = result["per_anchor"][0]
    assert east_result["hit"] == False, "EAST should miss"
    assert east_result["contrib"] == 0.0, "EAST contrib should be 0.0"
    assert result["anchor_score"] == 0.0, "Overall anchor score should be 0.0"
    
    print("✓ Miss test passed")


def test_shuffled_mode():
    """Test shuffled mode always misses."""
    head = "X" * 21 + "EAST" + "NORTHEAST" + "X" * 29 + "BERLINCLOCK" + "X"
    
    policy = {
        "anchor_scoring": {
            "mode": "shuffled",
            "anchors": [
                {"token": "EAST", "start": 21},
                {"token": "NORTHEAST", "start": 25},
                {"token": "BERLINCLOCK", "start": 63}
            ],
            "flexibility": {"r": 0, "typo_budget": 0},
            "weights": {
                "lambda_pos": 1.0,
                "lambda_typo": 1.0
            }
        }
    }
    
    result = score_anchors(head, policy)
    
    assert result["anchor_score"] == 0.0, f"Shuffled should score 0.0, got {result['anchor_score']}"
    for anchor in result["per_anchor"]:
        assert anchor["hit"] == False, f"{anchor['token']} should miss in shuffled"
        assert anchor["contrib"] == 0.0, f"{anchor['token']} contrib should be 0.0"
    
    print("✓ Shuffled mode test passed")


def test_combine_scores():
    """Test score combination changes across modes."""
    head = "X" * 21 + "EAST" + "NORTHEAST" + "X" * 29 + "BERLINCLOCK" + "X"
    
    # Fixed mode policy
    fixed_policy = {
        "anchor_scoring": {
            "mode": "fixed",
            "anchors": [
                {"token": "EAST", "start": 21},
                {"token": "NORTHEAST", "start": 25},
                {"token": "BERLINCLOCK", "start": 63}
            ],
            "flexibility": {"r": 0, "typo_budget": 0},
            "weights": {"lambda_pos": 1.0, "lambda_typo": 1.0}
        }
    }
    
    # Windowed mode policy (r=2)
    windowed_policy = {
        "anchor_scoring": {
            "mode": "windowed",
            "anchors": [
                {"token": "EAST", "start": 21},
                {"token": "NORTHEAST", "start": 25},
                {"token": "BERLINCLOCK", "start": 63}
            ],
            "flexibility": {"r": 2, "typo_budget": 1},
            "weights": {"lambda_pos": 1.0, "lambda_typo": 1.0}
        }
    }
    
    # Shuffled mode policy
    shuffled_policy = {
        "anchor_scoring": {
            "mode": "shuffled",
            "anchors": [
                {"token": "EAST", "start": 21},
                {"token": "NORTHEAST", "start": 25},
                {"token": "BERLINCLOCK", "start": 63}
            ],
            "flexibility": {"r": 0, "typo_budget": 0},
            "weights": {"lambda_pos": 1.0, "lambda_typo": 1.0}
        }
    }
    
    # Get anchor scores
    fixed_result = score_anchors(head, fixed_policy)
    windowed_result = score_anchors(head, windowed_policy)
    shuffled_result = score_anchors(head, shuffled_policy)
    
    # Mock language scores (same for all to isolate anchor effect)
    z_ngram = 0.5
    z_coverage = 0.3
    z_compress = 0.2
    weights = {
        "w_anchor": 0.15,
        "w_zngram": 0.45,
        "w_coverage": 0.25,
        "w_compress": 0.15
    }
    
    fixed_combined = combine_scores(fixed_result, z_ngram, z_coverage, z_compress, weights)
    windowed_combined = combine_scores(windowed_result, z_ngram, z_coverage, z_compress, weights)
    shuffled_combined = combine_scores(shuffled_result, z_ngram, z_coverage, z_compress, weights)
    
    # Fixed should score highest (perfect anchors)
    assert fixed_combined >= windowed_combined, f"Fixed ({fixed_combined}) should >= windowed ({windowed_combined})"
    assert fixed_combined > shuffled_combined, f"Fixed ({fixed_combined}) should > shuffled ({shuffled_combined})"
    # Windowed should score higher than shuffled
    assert windowed_combined > shuffled_combined, f"Windowed ({windowed_combined}) should > shuffled ({shuffled_combined})"
    
    # Check deltas make sense
    delta_fixed_windowed = abs(fixed_combined - windowed_combined)
    delta_fixed_shuffled = fixed_combined - shuffled_combined
    
    assert delta_fixed_windowed < 0.01, f"Delta fixed-windowed should be ~0 for perfect match, got {delta_fixed_windowed}"
    assert delta_fixed_shuffled > 0.0, f"Delta fixed-shuffled should be > 0, got {delta_fixed_shuffled}"
    
    print("✓ Combine scores test passed")


def test_hamming():
    """Test Hamming distance calculation."""
    assert hamming_distance("EAST", "EAST") == 0
    assert hamming_distance("EAST", "EAZT") == 1
    assert hamming_distance("EAST", "XXXX") == 4
    assert hamming_distance("EAST", "EASTS") == 4  # Different lengths
    print("✓ Hamming distance test passed")


def run_all_tests():
    """Run all unit tests."""
    print("\nRunning anchor scoring unit tests...")
    print("-" * 40)
    
    test_hamming()
    test_fixed_exact_hit()
    test_windowed_offset()
    test_windowed_typo()
    test_miss()
    test_shuffled_mode()
    test_combine_scores()
    
    print("-" * 40)
    print("✅ All tests passed!\n")


if __name__ == "__main__":
    run_all_tests()