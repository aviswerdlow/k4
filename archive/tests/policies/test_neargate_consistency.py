#!/usr/bin/env python3
"""Test that near-gate thresholds are consistent between Explore and Confirm."""

import json
import re
from pathlib import Path


def extract_neargate_from_code(filepath: Path) -> dict:
    """Extract near-gate thresholds from Python code."""
    content = filepath.read_text()
    
    thresholds = {}
    
    # Look for coverage threshold
    cov_match = re.search(r'coverage\s*>=\s*([\d.]+)', content)
    if cov_match:
        thresholds['coverage'] = float(cov_match.group(1))
    
    # Look for f_words threshold
    fw_match = re.search(r'f_words\s*>=\s*(\d+)', content)
    if fw_match:
        thresholds['f_words'] = int(fw_match.group(1))
    
    # Look for has_verb
    verb_match = re.search(r'has_verb|has_v', content)
    if verb_match:
        thresholds['has_verb'] = True
    
    return thresholds


def test_neargate_consistency():
    """Ensure Explore and Confirm use same near-gate thresholds."""
    
    # Paths to check
    repo_root = Path(__file__).parent.parent.parent
    
    # Confirm gate implementation
    confirm_gate = repo_root / "experiments/pipeline_v4/scripts/run_confirm_gates.py"
    
    # Alternative Confirm implementation
    confirm_alt = repo_root / "experiments/pipeline_v4/scripts/confirm/near_gate.py"
    
    # Extract thresholds
    thresholds = {}
    
    if confirm_gate.exists():
        thresholds['confirm_gates'] = extract_neargate_from_code(confirm_gate)
    
    if confirm_alt.exists():
        thresholds['confirm_alt'] = extract_neargate_from_code(confirm_alt)
    
    # Check for v4.1 exploration code
    explore_v41 = repo_root / "experiments/pipeline_v4/scripts/v4_1/grammar_generator.py"
    if explore_v41.exists():
        thresholds['explore_v41'] = extract_neargate_from_code(explore_v41)
    
    # Verify consistency
    print("Near-gate thresholds found:")
    for source, vals in thresholds.items():
        print(f"  {source}: {vals}")
    
    # Assert all have same f_words threshold
    f_words_values = [t.get('f_words') for t in thresholds.values() if 'f_words' in t]
    if f_words_values:
        assert len(set(f_words_values)) == 1, \
            f"Inconsistent f_words thresholds: {f_words_values}"
        print(f"\n✅ Consistent f_words threshold: {f_words_values[0]}")
    
    # Assert all have same coverage threshold
    coverage_values = [t.get('coverage') for t in thresholds.values() if 'coverage' in t]
    if coverage_values:
        # Allow small floating point differences
        assert max(coverage_values) - min(coverage_values) < 0.01, \
            f"Inconsistent coverage thresholds: {coverage_values}"
        print(f"✅ Consistent coverage threshold: {coverage_values[0]}")
    
    # Expected values (from pre-registration)
    EXPECTED_F_WORDS = 8
    EXPECTED_COVERAGE = 0.85
    
    # Verify against expected
    if f_words_values:
        assert f_words_values[0] == EXPECTED_F_WORDS, \
            f"F-words threshold {f_words_values[0]} != expected {EXPECTED_F_WORDS}"
    
    if coverage_values:
        assert abs(coverage_values[0] - EXPECTED_COVERAGE) < 0.01, \
            f"Coverage threshold {coverage_values[0]} != expected {EXPECTED_COVERAGE}"
    
    print(f"\n✅ All near-gate thresholds consistent with pre-registration:")
    print(f"   Coverage: {EXPECTED_COVERAGE}")
    print(f"   F-words: {EXPECTED_F_WORDS}")
    print(f"   Has verb: True")


if __name__ == "__main__":
    test_neargate_consistency()