#!/usr/bin/env python3
"""
Null Hypothesis Tests - Key scramble and segment shuffle
"""

import sys
import json
import random
from pathlib import Path
from typing import Dict, Any, List
import hashlib
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent / '03_SOLVERS'))
from zone_mask_v1.scripts.zone_runner import ZoneRunner

def scramble_key(key: str) -> str:
    """Scramble a key randomly"""
    chars = list(key)
    random.shuffle(chars)
    return ''.join(chars)

def score_english(text: str) -> float:
    """Score text for English-like properties"""
    if not text:
        return 0
    
    text = text.upper()
    score = 0
    
    # Common trigrams
    for tri in ['THE', 'AND', 'ING', 'HER', 'HAT', 'HIS', 'THA', 'ERE', 'FOR', 'ENT']:
        score += text.count(tri) * 3
    
    # Common bigrams
    for bi in ['TH', 'HE', 'IN', 'ER', 'AN', 'ED', 'ND', 'TO', 'EN', 'ES']:
        score += text.count(bi)
    
    return score / len(text)  # Normalize by length

def test_key_scramble(manifest_path: str, n_trials: int = 100):
    """Test with scrambled keys"""
    print("NULL HYPOTHESIS TEST: KEY SCRAMBLE")
    print("=" * 60)
    
    # Load manifest and ciphertext
    with open(manifest_path, 'r') as f:
        base_manifest = json.load(f)
    
    ct_path = Path(__file__).parent.parent / '02_DATA' / 'ciphertext_97.txt'
    with open(ct_path, 'r') as f:
        ciphertext = f.read().strip().upper()
    
    # Get baseline score with original keys
    runner = ZoneRunner()
    runner.manifest = base_manifest
    runner.ciphertext = ciphertext
    baseline_plaintext = runner.decrypt()
    baseline_score = score_english(baseline_plaintext)
    
    print(f"Baseline English score: {baseline_score:.4f}")
    
    # Run trials with scrambled keys
    scores = []
    for i in range(n_trials):
        test_manifest = json.loads(json.dumps(base_manifest))
        
        # Scramble each zone's key
        for zone in ['head', 'mid', 'tail']:
            if zone in test_manifest['cipher']['keys']:
                original_key = test_manifest['cipher']['keys'][zone]
                scrambled = scramble_key(original_key)
                test_manifest['cipher']['keys'][zone] = scrambled
        
        # Test with scrambled keys
        runner = ZoneRunner()
        runner.manifest = test_manifest
        runner.ciphertext = ciphertext
        
        try:
            plaintext = runner.decrypt()
            score = score_english(plaintext)
            scores.append(score)
        except:
            scores.append(0)
    
    # Statistical test
    better_count = sum(1 for s in scores if s >= baseline_score)
    p_value = (better_count + 1) / (n_trials + 1)
    
    # Holm correction for multiple tests (we have 2 tests)
    holm_p = min(p_value * 2, 1.0)
    
    print(f"\nResults from {n_trials} trials:")
    print(f"  Scrambled scores better than baseline: {better_count}/{n_trials}")
    print(f"  Raw p-value: {p_value:.6f}")
    print(f"  Holm-corrected p-value: {holm_p:.6f}")
    
    if holm_p < 0.01:
        print("✅ PASS: Solution significantly better than random keys (p < 0.01)")
    else:
        print("❌ FAIL: Solution not significantly better than random keys")
    
    return holm_p

def shuffle_segments(text: str, segment_size: int = 10) -> str:
    """Shuffle text in segments"""
    segments = [text[i:i+segment_size] for i in range(0, len(text), segment_size)]
    random.shuffle(segments)
    return ''.join(segments)

def test_segment_shuffle(manifest_path: str, n_trials: int = 100):
    """Test with shuffled ciphertext segments"""
    print("\nNULL HYPOTHESIS TEST: SEGMENT SHUFFLE")
    print("=" * 60)
    
    # Load manifest and ciphertext
    with open(manifest_path, 'r') as f:
        base_manifest = json.load(f)
    
    ct_path = Path(__file__).parent.parent / '02_DATA' / 'ciphertext_97.txt'
    with open(ct_path, 'r') as f:
        original_ct = f.read().strip().upper()
    
    # Get baseline score
    runner = ZoneRunner()
    runner.manifest = base_manifest
    runner.ciphertext = original_ct
    baseline_plaintext = runner.decrypt()
    baseline_score = score_english(baseline_plaintext)
    
    print(f"Baseline English score: {baseline_score:.4f}")
    
    # Run trials with shuffled segments
    scores = []
    for i in range(n_trials):
        shuffled_ct = shuffle_segments(original_ct, segment_size=7)
        
        runner = ZoneRunner()
        runner.manifest = base_manifest
        runner.ciphertext = shuffled_ct
        
        try:
            plaintext = runner.decrypt()
            score = score_english(plaintext)
            scores.append(score)
        except:
            scores.append(0)
    
    # Statistical test
    better_count = sum(1 for s in scores if s >= baseline_score)
    p_value = (better_count + 1) / (n_trials + 1)
    
    # Holm correction
    holm_p = min(p_value * 2, 1.0)
    
    print(f"\nResults from {n_trials} trials:")
    print(f"  Shuffled scores better than baseline: {better_count}/{n_trials}")
    print(f"  Raw p-value: {p_value:.6f}")
    print(f"  Holm-corrected p-value: {holm_p:.6f}")
    
    if holm_p < 0.01:
        print("✅ PASS: Solution significantly better than shuffled CT (p < 0.01)")
    else:
        print("❌ FAIL: Solution not significantly better than shuffled CT")
    
    return holm_p

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Null hypothesis tests')
    parser.add_argument('--manifest', required=True, help='Path to manifest')
    parser.add_argument('--test', choices=['key', 'segment', 'both'], default='both')
    parser.add_argument('--trials', type=int, default=100, help='Number of trials')
    
    args = parser.parse_args()
    
    if args.test in ['key', 'both']:
        p1 = test_key_scramble(args.manifest, args.trials)
    
    if args.test in ['segment', 'both']:
        p2 = test_segment_shuffle(args.manifest, args.trials)
    
    if args.test == 'both':
        print("\n" + "=" * 60)
        print("OVERALL RESULTS:")
        print(f"  Key scramble Holm p-value: {p1:.6f}")
        print(f"  Segment shuffle Holm p-value: {p2:.6f}")
        
        if p1 < 0.01 and p2 < 0.01:
            print("✅ BOTH TESTS PASS (p < 0.01)")
        else:
            print("❌ At least one test fails the p < 0.01 threshold")

if __name__ == '__main__':
    main()