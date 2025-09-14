#!/usr/bin/env python3
"""
Plan O: Fit homophonic cipher with anchor constraints
Uses simulated annealing to find optimal CT→PT mapping
"""

import sys
import os
import json
import random
import argparse
from typing import Dict, List, Tuple

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../03_SOLVERS/zone_mask_v1/scripts'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../07_TOOLS/language'))

from cipher_homophonic import AnchorConstrainedHomophonic
from scoring import LanguageScorer, score_text, find_words_in_text

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Anchor constraints (0-based indices)
ANCHORS = {
    "EAST": (21, 24),
    "NORTHEAST": (25, 33),
    "BERLIN": (63, 68),
    "CLOCK": (69, 73)
}

def check_anchors(text: str) -> bool:
    """Verify anchors are at correct positions"""
    if len(text) < 74:
        return False
    
    return (text[21:25] == "EAST" and
            text[25:34] == "NORTHEAST" and
            text[63:69] == "BERLIN" and
            text[69:74] == "CLOCK")

def extract_non_anchor_text(text: str) -> str:
    """Extract text outside anchor positions"""
    locked_positions = set()
    for anchor, (start, end) in ANCHORS.items():
        for i in range(start, end + 1):
            locked_positions.add(i)
    
    non_anchor = []
    for i, char in enumerate(text):
        if i not in locked_positions:
            non_anchor.append(char)
    
    return ''.join(non_anchor)

def run_homophonic_search(max_iterations: int = 100000, 
                         initial_temp: float = 1.0,
                         cooling_rate: float = 0.9999) -> Dict:
    """
    Run simulated annealing search for homophonic mapping
    
    Returns:
        Dictionary with best solution found
    """
    print("=" * 80)
    print("PLAN O: HOMOPHONIC CIPHER WITH ANCHOR CONSTRAINTS")
    print("=" * 80)
    print()
    
    # Initialize
    homophonic = AnchorConstrainedHomophonic(ANCHORS)
    scorer = LanguageScorer()
    
    print(f"Running simulated annealing for {max_iterations} iterations...")
    print(f"Initial temperature: {initial_temp}, Cooling rate: {cooling_rate}")
    print()
    
    # Run search
    best_pt, best_mapping = homophonic.simulated_annealing(
        K4_CIPHERTEXT,
        lambda x: scorer.combined_score(x),
        max_iterations=max_iterations,
        initial_temp=initial_temp,
        cooling_rate=cooling_rate
    )
    
    # Verify anchors
    if not check_anchors(best_pt):
        print("❌ ERROR: Anchors not preserved!")
        return None
    
    # Extract results
    non_anchor_text = extract_non_anchor_text(best_pt)
    words_found = find_words_in_text(non_anchor_text)
    score = scorer.combined_score(non_anchor_text)
    
    # Display results
    print("\n" + "=" * 80)
    print("BEST SOLUTION FOUND")
    print("=" * 80)
    
    print(f"\nPlaintext preview:")
    print(f"  [0:21]: {best_pt[0:21]}")
    print(f"  [21:34]: {best_pt[21:34]} (anchors)")
    print(f"  [34:63]: {best_pt[34:63]}")
    print(f"  [63:74]: {best_pt[63:74]} (anchors)")
    print(f"  [74:97]: {best_pt[74:97]}")
    
    print(f"\nNon-anchor text analysis:")
    print(f"  Score: {score:.2f}")
    print(f"  Words found: {len(words_found)}")
    if words_found:
        print(f"  Sample words: {', '.join(words_found[:10])}")
    
    # Check for function words
    function_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL'}
    found_functions = [w for w in words_found if w in function_words]
    if found_functions:
        print(f"  ✅ Function words found: {', '.join(found_functions)}")
    else:
        print(f"  ❌ No function words found")
    
    result = {
        "plaintext": best_pt,
        "mapping": best_mapping,
        "score": score,
        "words_found": words_found,
        "anchors_valid": True,
        "has_function_words": len(found_functions) > 0
    }
    
    return result

def generate_null_scores(text: str, num_nulls: int = 100) -> List[float]:
    """Generate null distribution scores for significance testing"""
    scorer = LanguageScorer()
    non_anchor = extract_non_anchor_text(text)
    scores = []
    
    for _ in range(num_nulls):
        # Shuffle non-anchor text
        shuffled = list(non_anchor)
        random.shuffle(shuffled)
        score = scorer.combined_score(''.join(shuffled))
        scores.append(score)
    
    return scores

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Homophonic cipher solver with anchors')
    parser.add_argument('--max_iterations', type=int, default=250000,
                       help='Maximum iterations for simulated annealing')
    parser.add_argument('--initial_temp', type=float, default=1.0,
                       help='Initial temperature')
    parser.add_argument('--cooling_rate', type=float, default=0.99995,
                       help='Temperature cooling rate')
    parser.add_argument('--num_runs', type=int, default=3,
                       help='Number of independent runs')
    
    args = parser.parse_args()
    
    best_overall = None
    best_score = -float('inf')
    
    # Run multiple times with different random starts
    for run in range(args.num_runs):
        print(f"\n{'='*80}")
        print(f"RUN {run + 1} OF {args.num_runs}")
        print(f"{'='*80}")
        
        result = run_homophonic_search(
            max_iterations=args.max_iterations,
            initial_temp=args.initial_temp,
            cooling_rate=args.cooling_rate
        )
        
        if result and result['score'] > best_score:
            best_score = result['score']
            best_overall = result
    
    # Final summary
    if best_overall:
        print("\n" + "=" * 80)
        print("FINAL SUMMARY")
        print("=" * 80)
        
        # Test against nulls
        null_scores = generate_null_scores(K4_CIPHERTEXT, 100)
        mean_null = sum(null_scores) / len(null_scores)
        std_null = (sum((x - mean_null)**2 for x in null_scores) / len(null_scores)) ** 0.5
        z_score = (best_overall['score'] - mean_null) / std_null if std_null > 0 else 0
        
        print(f"\nBest solution score: {best_overall['score']:.2f}")
        print(f"Null mean: {mean_null:.2f}, Null std: {std_null:.2f}")
        print(f"Z-score: {z_score:.2f}")
        
        if z_score > 3:
            print("✅ Significantly better than null (>3σ)")
        else:
            print("❌ Not significantly better than null")
        
        # Save result
        if best_overall['has_function_words'] and z_score > 3:
            output_file = 'homophonic_solution.json'
            with open(output_file, 'w') as f:
                json.dump(best_overall, f, indent=2)
            print(f"\n✅ Solution saved to {output_file}")
        else:
            print("\n❌ Solution does not meet acceptance criteria")
    else:
        print("\n❌ No valid solution found")

if __name__ == "__main__":
    main()