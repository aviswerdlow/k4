#!/usr/bin/env python3
"""
Empirical p-value calculation through permutation testing
No parametric assumptions, honest null distributions
"""

import random
import numpy as np
from typing import Dict, List, Tuple
from collections import Counter
import multiprocessing as mp
from functools import partial

def generate_yoked_null_shuffle(ciphertext: str, 
                               anchor_positions: Dict[str, Tuple[int, int]]) -> str:
    """
    Generate null by shuffling CT outside anchor positions
    Preserves anchor structure exactly
    """
    ct_list = list(ciphertext)
    
    # Identify non-anchor positions
    locked = set()
    for start, end in anchor_positions.values():
        for i in range(start, end + 1):
            locked.add(i)
    
    # Extract and shuffle non-anchor characters
    non_anchor_chars = []
    non_anchor_positions = []
    for i, char in enumerate(ct_list):
        if i not in locked:
            non_anchor_chars.append(char)
            non_anchor_positions.append(i)
    
    random.shuffle(non_anchor_chars)
    
    # Place back shuffled characters
    for pos, char in zip(non_anchor_positions, non_anchor_chars):
        ct_list[pos] = char
    
    return ''.join(ct_list)

def generate_random_homophonic_mapping(alphabet: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                                      target_complexity: float = 10.0) -> Dict[str, str]:
    """
    Generate random homophonic mapping with controlled complexity
    """
    mapping = {}
    available_pt = list(alphabet)
    
    # Start with 1-1 mapping
    for ct in alphabet:
        if available_pt:
            pt = random.choice(available_pt)
            mapping[ct] = pt
            if random.random() < 0.3:  # 30% chance to reuse
                available_pt.append(pt)  # Allow reuse (homophone)
            else:
                available_pt.remove(pt)
        else:
            # All used, pick random
            mapping[ct] = random.choice(list(alphabet))
    
    return mapping

def compute_null_score(args):
    """
    Worker function for parallel null computation
    """
    null_type, ciphertext, anchor_positions, scorer, homophonic = args
    
    if null_type == 'shuffle':
        # Shuffle null
        null_ct = generate_yoked_null_shuffle(ciphertext, anchor_positions)
        # Decrypt with current best mapping
        if homophonic and hasattr(homophonic, 'decrypt_with_anchors'):
            from cipher_homophonic import AnchorConstrainedHomophonic
            h = AnchorConstrainedHomophonic(anchor_positions)
            # Use a random mapping for null
            random_mapping = generate_random_homophonic_mapping()
            null_pt = h.decrypt_with_anchors(null_ct, random_mapping)
        else:
            null_pt = null_ct  # Fallback
    else:
        # Random mapping null
        from cipher_homophonic import AnchorConstrainedHomophonic
        h = AnchorConstrainedHomophonic(anchor_positions)
        random_mapping = generate_random_homophonic_mapping()
        null_pt = h.decrypt_with_anchors(ciphertext, random_mapping)
    
    # Score with masked anchors
    score = scorer.score_masked(null_pt, anchor_positions)
    return score

def calculate_empirical_pvalue(observed_score: float,
                              ciphertext: str,
                              anchor_positions: Dict[str, Tuple[int, int]],
                              scorer,
                              num_nulls: int = 5000,
                              null_type: str = 'both',
                              parallel: bool = True) -> Dict:
    """
    Calculate empirical p-value through permutation testing
    
    Args:
        observed_score: Score of the candidate solution
        ciphertext: Original K4 ciphertext
        anchor_positions: Anchor constraint positions
        scorer: HardenedScorer instance
        num_nulls: Number of null permutations
        null_type: 'shuffle', 'random_map', or 'both'
        parallel: Use parallel processing
    
    Returns:
        Dictionary with p-value and null distribution stats
    """
    null_scores = []
    
    # Prepare arguments for parallel processing
    if null_type == 'both':
        # Half shuffle, half random mapping
        args_list = []
        for i in range(num_nulls // 2):
            args_list.append(('shuffle', ciphertext, anchor_positions, scorer, None))
        for i in range(num_nulls // 2):
            args_list.append(('random_map', ciphertext, anchor_positions, scorer, None))
    else:
        args_list = [(null_type, ciphertext, anchor_positions, scorer, None) 
                     for _ in range(num_nulls)]
    
    if parallel and num_nulls > 100:
        # Use multiprocessing for large null sets
        with mp.Pool(processes=mp.cpu_count()) as pool:
            null_scores = pool.map(compute_null_score, args_list)
    else:
        # Sequential for small sets or debugging
        for args in args_list:
            null_scores.append(compute_null_score(args))
    
    # Calculate empirical p-value
    null_scores = np.array(null_scores)
    p_value = np.mean(null_scores >= observed_score)
    
    # Calculate statistics
    results = {
        'observed_score': observed_score,
        'p_value': p_value,
        'num_nulls': num_nulls,
        'null_mean': np.mean(null_scores),
        'null_std': np.std(null_scores),
        'null_min': np.min(null_scores),
        'null_max': np.max(null_scores),
        'null_percentiles': {
            '95': np.percentile(null_scores, 95),
            '99': np.percentile(null_scores, 99),
            '99.9': np.percentile(null_scores, 99.9)
        },
        'z_score': (observed_score - np.mean(null_scores)) / np.std(null_scores) if np.std(null_scores) > 0 else 0,
        'significant': p_value <= 0.001
    }
    
    return results

def bonferroni_correction(p_values: List[float], num_seeds: int, num_temps: int) -> Dict:
    """
    Apply Bonferroni correction for multiple testing
    """
    num_tests = num_seeds * num_temps
    min_p = min(p_values)
    
    corrected_p = min(1.0, min_p * num_tests)
    
    return {
        'min_p_uncorrected': min_p,
        'num_tests': num_tests,
        'bonferroni_p': corrected_p,
        'significant': corrected_p <= 0.001,
        'all_p_values': p_values
    }

def holdout_validation(plaintext: str, mapping: Dict[str, str],
                      ciphertext: str, anchor_positions: Dict[str, Tuple[int, int]],
                      scorer) -> Dict:
    """
    Perform hold-out validation on odd/even indices
    """
    # Extract non-anchor positions
    locked = set()
    for start, end in anchor_positions.values():
        for i in range(start, end + 1):
            locked.add(i)
    
    non_anchor_positions = [i for i in range(len(plaintext)) if i not in locked]
    
    # Split into odd/even
    odd_positions = [p for p in non_anchor_positions if p % 2 == 1]
    even_positions = [p for p in non_anchor_positions if p % 2 == 0]
    
    # Create masked texts
    odd_text = list(plaintext)
    even_text = list(plaintext)
    
    for pos in even_positions:
        odd_text[pos] = 'X'  # Mask even in odd text
    for pos in odd_positions:
        even_text[pos] = 'X'  # Mask odd in even text
    
    odd_text = ''.join(odd_text)
    even_text = ''.join(even_text)
    
    # Score both
    odd_score = scorer.score_masked(odd_text, anchor_positions, mapping)
    even_score = scorer.score_masked(even_text, anchor_positions, mapping)
    full_score = scorer.score_masked(plaintext, anchor_positions, mapping)
    
    # Check consistency
    score_ratio = min(odd_score, even_score) / max(odd_score, even_score) if max(odd_score, even_score) > 0 else 0
    
    return {
        'odd_score': odd_score,
        'even_score': even_score,
        'full_score': full_score,
        'score_ratio': score_ratio,
        'consistent': score_ratio > 0.7,  # Scores should be similar
        'both_positive': odd_score > 0 and even_score > 0
    }

def compression_test(plaintext: str, anchor_positions: Dict[str, Tuple[int, int]]) -> Dict:
    """
    Test if plaintext compresses better than random with same letter distribution
    """
    import lzma
    
    # Extract non-anchor text
    locked = set()
    for start, end in anchor_positions.values():
        for i in range(start, end + 1):
            locked.add(i)
    
    non_anchor = ''.join([plaintext[i] for i in range(len(plaintext)) if i not in locked])
    
    # Compress original
    original_compressed = len(lzma.compress(non_anchor.encode()))
    
    # Generate random permutations with same letter counts
    random_scores = []
    for _ in range(100):
        shuffled = list(non_anchor)
        random.shuffle(shuffled)
        random_compressed = len(lzma.compress(''.join(shuffled).encode()))
        random_scores.append(random_compressed)
    
    # Calculate ratio
    avg_random = np.mean(random_scores)
    compression_ratio = original_compressed / avg_random if avg_random > 0 else 1
    
    return {
        'original_size': len(non_anchor),
        'compressed_size': original_compressed,
        'avg_random_compressed': avg_random,
        'compression_ratio': compression_ratio,
        'better_than_random': compression_ratio < 0.95  # 5% better compression
    }

if __name__ == "__main__":
    # Test empirical p-value calculation
    from hardened_scorer import HardenedScorer
    
    scorer = HardenedScorer()
    
    anchors = {
        "EAST": (21, 24),
        "NORTHEAST": (25, 33),
        "BERLIN": (63, 68),
        "CLOCK": (69, 73)
    }
    
    K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
    
    # Test with a random score
    test_score = 100.0
    
    print("Calculating empirical p-value...")
    results = calculate_empirical_pvalue(
        test_score, K4, anchors, scorer, 
        num_nulls=1000, null_type='both', parallel=False
    )
    
    print(f"\nObserved score: {test_score}")
    print(f"Null mean: {results['null_mean']:.2f} ± {results['null_std']:.2f}")
    print(f"P-value: {results['p_value']:.4f}")
    print(f"Significant: {results['significant']}")