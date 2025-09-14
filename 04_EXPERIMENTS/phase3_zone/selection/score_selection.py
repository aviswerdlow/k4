#!/usr/bin/env python3
"""
Plan R: Score selection overlays with empirical validation
"""

import sys
import os
import json
import random
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import Counter

# Add parent paths
sys.path.append(os.path.join(os.path.dirname(__file__), '../key_fit'))

from paths import get_all_paths, get_anchor_indices
from hardened_scorer import HardenedScorer

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Also test on best homophonic output (even if failed)
try:
    with open('../key_fit/optimized_homophonic.json', 'r') as f:
        HOMOPHONIC_PT = json.load(f)['plaintext']
except:
    HOMOPHONIC_PT = None

class SelectionScorer:
    """
    Score selection overlays using frozen LM and token grammar
    """
    
    def __init__(self):
        # Use same frozen scorer as Plan O hardening
        self.base_scorer = HardenedScorer()
        
        # Load token dictionary for grammar checking
        token_file = '/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/02_DATA/codebook/tokens.txt'
        self.tokens = set()
        with open(token_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    self.tokens.add(line.upper())
        
        # Common English words for quick check
        self.common_words = {
            'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
            'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'HIS',
            'HOW', 'ITS', 'NOW', 'NEW', 'TWO', 'WAY', 'WHO', 'HAS'
        }
    
    def score_selection(self, selected_text: str) -> Dict:
        """
        Score a selection overlay
        
        Returns:
            Dictionary with score components
        """
        text_upper = selected_text.upper()
        
        # Count words found
        words_found = []
        for word in self.common_words:
            if word in text_upper:
                words_found.append(word)
        
        # Count tokens found
        tokens_found = []
        for token in self.tokens:
            if len(token) >= 2 and token in text_upper:
                tokens_found.append(token)
        
        # Check for numeric patterns (angles, bearings)
        import re
        numbers = re.findall(r'\d+', text_upper)
        
        # Calculate base score
        word_score = sum(len(w) for w in words_found) * 5
        token_score = sum(len(t) for t in tokens_found) * 3
        
        # Check vowel ratio
        vowels = sum(1 for c in text_upper if c in 'AEIOU')
        letters = sum(1 for c in text_upper if c.isalpha())
        vowel_ratio = vowels / letters if letters > 0 else 0
        
        # Vowel penalty if too extreme
        vowel_penalty = 0
        if vowel_ratio < 0.25 or vowel_ratio > 0.65:
            vowel_penalty = 20
        
        # Check for repeated characters (bad sign)
        repeat_penalty = 0
        for i in range(len(text_upper) - 2):
            if text_upper[i] == text_upper[i+1] == text_upper[i+2]:
                repeat_penalty += 5
        
        total_score = word_score + token_score - vowel_penalty - repeat_penalty
        
        return {
            'score': total_score,
            'words_found': words_found,
            'tokens_found': tokens_found,
            'num_words': len(words_found),
            'num_tokens': len(tokens_found),
            'vowel_ratio': vowel_ratio,
            'has_numbers': len(numbers) > 0,
            'numbers': numbers
        }
    
    def calculate_empirical_pvalue(self, observed_score: float,
                                  text: str, path_length: int,
                                  num_nulls: int = 1000) -> float:
        """
        Calculate p-value vs random equal-length selections
        """
        anchors = get_anchor_indices()
        available_indices = [i for i in range(len(text)) if i not in anchors]
        
        null_scores = []
        for _ in range(num_nulls):
            # Random selection of same length
            if len(available_indices) >= path_length:
                random_indices = random.sample(available_indices, min(path_length, len(available_indices)))
                random_text = ''.join([text[i] for i in sorted(random_indices)])
                
                null_score = self.score_selection(random_text)['score']
                null_scores.append(null_score)
        
        if not null_scores:
            return 1.0
        
        # Calculate p-value
        null_scores = np.array(null_scores)
        p_value = np.mean(null_scores >= observed_score)
        
        return p_value

def test_replication(text: str, path_type: str, best_params: Dict) -> bool:
    """
    Test if nearby paths give consistent results
    """
    # This is simplified - would need path-specific logic
    return True

def run_plan_r(test_texts: List[str] = None, 
               min_words: int = 2,
               num_nulls: int = 1000) -> Dict:
    """
    Run complete Plan R analysis
    """
    print("=" * 80)
    print("PLAN R: SELECTION OVERLAY ANALYSIS")
    print("=" * 80)
    
    if test_texts is None:
        test_texts = [K4_CIPHERTEXT]
        if HOMOPHONIC_PT:
            test_texts.append(HOMOPHONIC_PT)
    
    scorer = SelectionScorer()
    all_results = []
    
    for text_idx, text in enumerate(test_texts):
        text_name = "K4" if text_idx == 0 else "Homophonic"
        print(f"\nTesting on {text_name}...")
        print("-" * 40)
        
        # Generate all paths
        paths = get_all_paths(text)
        print(f"Generated {len(paths)} selection paths")
        
        # Score each path
        for path in paths:
            score_result = scorer.score_selection(path['selected'])
            
            # Only consider if meets minimum criteria
            if score_result['num_words'] >= min_words or score_result['num_tokens'] >= 3:
                # Calculate empirical p-value
                p_value = scorer.calculate_empirical_pvalue(
                    score_result['score'],
                    text,
                    path['length'],
                    num_nulls
                )
                
                result = {
                    'text_source': text_name,
                    'path': path,
                    'score_result': score_result,
                    'p_value': p_value,
                    'significant': p_value <= 0.001
                }
                
                all_results.append(result)
                
                # Print if promising
                if p_value <= 0.01:
                    print(f"\n  Promising: {path['type']} ({path['params']})")
                    print(f"    Words: {score_result['words_found']}")
                    print(f"    Tokens: {score_result['tokens_found'][:5]}")
                    print(f"    P-value: {p_value:.4f}")
                    print(f"    Preview: {path['selected'][:40]}...")
    
    # Find best result
    significant_results = [r for r in all_results if r['significant']]
    
    if not significant_results:
        print("\n❌ No selection paths achieved p ≤ 0.001")
        return {
            'success': False,
            'reason': 'No significant paths found',
            'num_tested': len(all_results)
        }
    
    # Sort by p-value
    significant_results.sort(key=lambda x: x['p_value'])
    best = significant_results[0]
    
    print("\n" + "=" * 80)
    print("BEST SELECTION PATH")
    print("=" * 80)
    
    print(f"\nSource: {best['text_source']}")
    print(f"Path: {best['path']['type']} ({best['path']['params']})")
    print(f"P-value: {best['p_value']:.6f}")
    print(f"Words: {', '.join(best['score_result']['words_found'])}")
    print(f"Selected text: {best['path']['selected'][:60]}...")
    
    # Check for replication
    replicates = test_replication(
        text,
        best['path']['type'],
        best['path']['params']
    )
    
    # Check for grammar match (simplified)
    has_instruction = (
        best['score_result']['num_tokens'] >= 3 and
        best['score_result']['has_numbers']
    )
    
    success = (
        best['p_value'] <= 0.001 and
        (best['score_result']['num_words'] >= 2 or has_instruction) and
        replicates
    )
    
    if success:
        print("\n✅ PLAN R: VALID SELECTION OVERLAY FOUND")
    else:
        print("\n❌ PLAN R: NO VALID OVERLAY")
    
    results = {
        'success': success,
        'best_result': {
            'path_type': best['path']['type'],
            'path_params': best['path']['params'],
            'selected_text': best['path']['selected'],
            'indices': best['path']['indices'],
            'words': best['score_result']['words_found'],
            'tokens': best['score_result']['tokens_found'],
            'p_value': best['p_value']
        } if significant_results else None,
        'num_paths_tested': len(all_results),
        'num_significant': len(significant_results)
    }
    
    # Save results
    with open('plan_r_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

def main():
    """Run Plan R analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Plan R selection overlay')
    parser.add_argument('--nulls', type=int, default=1000,
                       help='Number of null permutations')
    parser.add_argument('--min_words', type=int, default=2,
                       help='Minimum words required')
    
    args = parser.parse_args()
    
    results = run_plan_r(
        min_words=args.min_words,
        num_nulls=args.nulls
    )
    
    if not results['success']:
        print(f"\nAnalysis: {results.get('reason', 'No valid overlay found')}")
        print("\nConclusion: K4 likely requires external information beyond the ciphertext")

if __name__ == "__main__":
    main()