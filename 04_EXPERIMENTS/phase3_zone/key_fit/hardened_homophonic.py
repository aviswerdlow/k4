#!/usr/bin/env python3
"""
Hardened homophonic cipher with full validation protocol
Implements all safeguards against overfitting
"""

import sys
import os
import json
import random
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import multiprocessing as mp
from datetime import datetime
import hashlib

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../03_SOLVERS/zone_mask_v1/scripts'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../07_TOOLS/language'))

from cipher_homophonic import AnchorConstrainedHomophonic
from hardened_scorer import HardenedScorer, validate_solution
from empirical_pvalue import (
    calculate_empirical_pvalue, 
    bonferroni_correction,
    holdout_validation,
    compression_test
)

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Anchor constraints
ANCHORS = {
    "EAST": (21, 24),
    "NORTHEAST": (25, 33),
    "BERLIN": (63, 68),
    "CLOCK": (69, 73)
}

def run_single_seed(args):
    """
    Run a single seed optimization
    Worker function for parallel processing
    """
    seed_num, iterations, temp, cooling = args
    
    random.seed(seed_num)
    np.random.seed(seed_num)
    
    scorer = HardenedScorer()
    homophonic = AnchorConstrainedHomophonic(ANCHORS)
    
    # Run annealing with masked scoring
    def masked_scorer(text):
        return scorer.score_masked(text, ANCHORS)
    
    best_pt, best_mapping = homophonic.simulated_annealing(
        K4_CIPHERTEXT,
        masked_scorer,
        max_iterations=iterations,
        initial_temp=temp,
        cooling_rate=cooling
    )
    
    # Validate solution
    validation = validate_solution(best_pt, best_mapping, K4_CIPHERTEXT, ANCHORS)
    
    return {
        'seed': seed_num,
        'plaintext': best_pt,
        'mapping': best_mapping,
        'validation': validation,
        'params': {
            'iterations': iterations,
            'temp': temp,
            'cooling': cooling
        }
    }

def check_replication(solutions: List[Dict], min_replications: int = 3) -> Dict:
    """
    Check if solutions replicate across seeds
    """
    # Group by similar plaintexts (edit distance)
    def edit_distance(s1, s2):
        if len(s1) != len(s2):
            return max(len(s1), len(s2))
        return sum(c1 != c2 for c1, c2 in zip(s1, s2))
    
    clusters = []
    for sol in solutions:
        if not sol['validation']['passes_all']:
            continue
        
        pt = sol['plaintext']
        found_cluster = False
        
        for cluster in clusters:
            # Check if similar to cluster representative
            if edit_distance(pt, cluster['representative']) <= 5:
                cluster['members'].append(sol)
                found_cluster = True
                break
        
        if not found_cluster:
            clusters.append({
                'representative': pt,
                'members': [sol]
            })
    
    # Find clusters with enough replications
    replicated = []
    for cluster in clusters:
        if len(cluster['members']) >= min_replications:
            replicated.append(cluster)
    
    return {
        'num_clusters': len(clusters),
        'replicated_clusters': replicated,
        'has_replication': len(replicated) > 0,
        'best_cluster': max(replicated, key=lambda c: len(c['members'])) if replicated else None
    }

def run_hardened_optimization(num_seeds: int = 20, 
                            iterations_per_seed: int = 200000,
                            parallel: bool = True) -> Dict:
    """
    Run the complete hardened optimization protocol
    """
    print("=" * 80)
    print("HARDENED HOMOPHONIC OPTIMIZATION PROTOCOL")
    print("=" * 80)
    
    scorer = HardenedScorer()
    print(f"\nScorer hash (frozen): {scorer.get_scorer_hash()}")
    
    # Generate parameter combinations
    args_list = []
    for seed in range(num_seeds):
        # Vary parameters for diversity
        temp = random.uniform(0.8, 2.0)
        cooling = random.uniform(0.9999, 0.99998)
        args_list.append((seed, iterations_per_seed, temp, cooling))
    
    print(f"\nRunning {num_seeds} seeds × {iterations_per_seed} iterations...")
    print("This will take several minutes...\n")
    
    # Run optimizations
    if parallel:
        with mp.Pool(processes=min(mp.cpu_count(), num_seeds)) as pool:
            solutions = pool.map(run_single_seed, args_list)
    else:
        solutions = []
        for i, args in enumerate(args_list):
            print(f"  Seed {i+1}/{num_seeds}...", end=" ")
            sol = run_single_seed(args)
            solutions.append(sol)
            if sol['validation']['passes_all']:
                print("✓ (passes constraints)")
            else:
                print("✗ (fails constraints)")
    
    # Filter passing solutions
    passing = [s for s in solutions if s['validation']['passes_all']]
    print(f"\n{len(passing)}/{num_seeds} seeds passed linguistic constraints")
    
    if not passing:
        print("\n❌ No solutions passed the hardened constraints")
        return {
            'success': False,
            'reason': 'No solutions passed linguistic constraints'
        }
    
    # Check replication
    print("\nChecking replication across seeds...")
    replication = check_replication(passing, min_replications=3)
    
    if not replication['has_replication']:
        print("❌ No solution replicated across ≥3 seeds")
        return {
            'success': False,
            'reason': 'No replication across seeds',
            'passing_count': len(passing)
        }
    
    print(f"✓ Found {len(replication['replicated_clusters'])} replicated solution(s)")
    
    # Take best replicated solution
    best_cluster = replication['best_cluster']
    best_solution = max(best_cluster['members'], 
                        key=lambda s: s['validation']['masked_score'])
    
    print(f"\nBest replicated solution (from {len(best_cluster['members'])} seeds):")
    print(f"  Score: {best_solution['validation']['masked_score']:.2f}")
    print(f"  Complexity: {best_solution['validation']['mapping_complexity']:.2f}")
    
    # Calculate empirical p-value
    print("\nCalculating empirical p-value (5000 nulls)...")
    pvalue_results = calculate_empirical_pvalue(
        best_solution['validation']['masked_score'],
        K4_CIPHERTEXT,
        ANCHORS,
        scorer,
        num_nulls=5000,
        null_type='both',
        parallel=parallel
    )
    
    print(f"  Observed: {pvalue_results['observed_score']:.2f}")
    print(f"  Null mean: {pvalue_results['null_mean']:.2f} ± {pvalue_results['null_std']:.2f}")
    print(f"  P-value: {pvalue_results['p_value']:.6f}")
    
    # Apply Bonferroni correction
    all_p_values = [pvalue_results['p_value']]  # Could add more if we tested multiple
    bonferroni = bonferroni_correction(all_p_values, num_seeds, 1)
    
    print(f"  Bonferroni-corrected p: {bonferroni['bonferroni_p']:.6f}")
    
    if not bonferroni['significant']:
        print("❌ Not significant after multiple testing correction")
        return {
            'success': False,
            'reason': 'Not significant after correction',
            'p_value': pvalue_results['p_value'],
            'corrected_p': bonferroni['bonferroni_p']
        }
    
    # Hold-out validation
    print("\nPerforming hold-out validation...")
    holdout = holdout_validation(
        best_solution['plaintext'],
        best_solution['mapping'],
        K4_CIPHERTEXT,
        ANCHORS,
        scorer
    )
    
    print(f"  Odd indices score: {holdout['odd_score']:.2f}")
    print(f"  Even indices score: {holdout['even_score']:.2f}")
    print(f"  Consistency: {holdout['consistent']}")
    
    if not holdout['both_positive']:
        print("❌ Failed hold-out validation")
        return {
            'success': False,
            'reason': 'Failed hold-out validation'
        }
    
    # Compression test
    print("\nPerforming compression test...")
    compression = compression_test(best_solution['plaintext'], ANCHORS)
    
    print(f"  Compression ratio: {compression['compression_ratio']:.3f}")
    print(f"  Better than random: {compression['better_than_random']}")
    
    # Final sanity check: Remove anchors and re-score
    print("\nAnchor removal sanity check...")
    masked_pt = list(best_solution['plaintext'])
    for start, end in ANCHORS.values():
        for i in range(start, end + 1):
            masked_pt[i] = 'X'
    masked_pt = ''.join(masked_pt)
    
    anchor_removed_score = scorer.score_masked(masked_pt, ANCHORS)
    score_drop = (best_solution['validation']['masked_score'] - anchor_removed_score) / best_solution['validation']['masked_score']
    
    print(f"  Score without anchors: {anchor_removed_score:.2f}")
    print(f"  Score drop: {score_drop:.1%}")
    
    if score_drop < 0.5:
        print("⚠️ Warning: Score doesn't drop much without anchors (possible leakage)")
    
    # Compile final results
    print("\n" + "=" * 80)
    print("FINAL VALIDATION RESULTS")
    print("=" * 80)
    
    success = (
        best_solution['validation']['passes_all'] and
        bonferroni['significant'] and
        holdout['both_positive'] and
        replication['has_replication']
    )
    
    if success:
        print("\n✅ SOLUTION PASSES ALL HARDENED VALIDATION CRITERIA")
    else:
        print("\n❌ SOLUTION FAILS HARDENED VALIDATION")
    
    results = {
        'success': success,
        'scorer_hash': scorer.get_scorer_hash(),
        'best_solution': {
            'plaintext': best_solution['plaintext'],
            'mapping': best_solution['mapping'],
            'score': best_solution['validation']['masked_score'],
            'complexity': best_solution['validation']['mapping_complexity']
        },
        'validation': {
            'linguistic_constraints': best_solution['validation']['constraint_details'],
            'p_value': pvalue_results['p_value'],
            'corrected_p': bonferroni['bonferroni_p'],
            'replication_count': len(best_cluster['members']),
            'holdout': holdout,
            'compression': compression
        },
        'metadata': {
            'num_seeds': num_seeds,
            'iterations_per_seed': iterations_per_seed,
            'passing_seeds': len(passing),
            'timestamp': datetime.now().isoformat()
        }
    }
    
    # Save results
    output_file = 'hardened_homophonic_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    # Display plaintext if successful
    if success:
        pt = best_solution['plaintext']
        print(f"\nValidated plaintext:")
        print(f"  [0:21]: {pt[0:21]}")
        print(f"  [21:34]: {pt[21:34]} (anchors)")
        print(f"  [34:63]: {pt[34:63]}")
        print(f"  [63:74]: {pt[63:74]} (anchors)")
        print(f"  [74:97]: {pt[74:97]}")
        
        print(f"\nContent words (≥5 letters): {', '.join(best_solution['validation']['constraint_details']['content_words_5plus'])}")
        print(f"Function words: {', '.join(best_solution['validation']['constraint_details']['function_words'])}")
    
    return results

def main():
    """Run the hardened protocol"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hardened homophonic optimization')
    parser.add_argument('--seeds', type=int, default=20,
                       help='Number of seeds to run (default: 20)')
    parser.add_argument('--iterations', type=int, default=200000,
                       help='Iterations per seed (default: 200000)')
    parser.add_argument('--sequential', action='store_true',
                       help='Run sequentially instead of parallel')
    
    args = parser.parse_args()
    
    results = run_hardened_optimization(
        num_seeds=args.seeds,
        iterations_per_seed=args.iterations,
        parallel=not args.sequential
    )
    
    if not results['success']:
        print(f"\n🔍 Analysis: {results.get('reason', 'Unknown failure')}")
        print("\nPlan O likely does not have a valid homophonic solution under honest scoring.")
        print("Consider:")
        print("  1. Plan P: Token segmentation on whatever output we have")
        print("  2. Plan R: Selection overlay patterns")
        print("  3. External information hypotheses with tight constraints")

if __name__ == "__main__":
    main()