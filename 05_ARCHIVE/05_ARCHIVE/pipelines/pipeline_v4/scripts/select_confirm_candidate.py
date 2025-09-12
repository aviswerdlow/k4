#!/usr/bin/env python3
"""Deterministically select one candidate for Confirm phase."""

import json
import csv
from pathlib import Path


def compute_ranking_key(candidate, explore_matrix_row):
    """Compute the 8-part ranking key for a candidate."""
    
    # k1: Window-robust delta (maximize)
    k1 = min(
        candidate['deltas']['r2'],
        candidate['deltas']['r3'],
        candidate['deltas']['r4']
    )
    
    # k2: Shuffled margin (maximize)
    k2 = candidate['deltas']['shuffled']
    
    # k3: Coverage from head-gate metrics (maximize)
    # Using coverage_post from EXPLORE_MATRIX
    k3 = float(explore_matrix_row['cov_post'])
    
    # k4: Statistical strength (more negative is better)
    k4 = -max(
        candidate['holm']['coverage']['p_holm'],
        candidate['holm']['f_words']['p_holm']
    )
    
    # k5: Orbit isolation (more negative is better)
    k5 = -candidate['orbit']['tie_fraction']
    
    # k6: Verb robustness (maximize)
    # Using verb_post from EXPLORE_MATRIX
    k6 = int(explore_matrix_row['verb_post'])
    
    # k7: Function words (maximize)
    # Using fw_post from EXPLORE_MATRIX
    k7 = int(explore_matrix_row['fw_post'])
    
    # k8: Tiebreaker - seed (smaller first)
    k8 = -candidate['seed_u64']  # Negate so smaller is better in max sort
    
    return (k1, k2, k3, k4, k5, k6, k7, k8)


def main():
    # Load promotion queue
    queue_path = Path("experiments/pipeline_v4/runs/v4_1_1/k200/promotion_queue.json")
    with open(queue_path) as f:
        queue = json.load(f)
    
    # Load EXPLORE_MATRIX for additional metrics
    matrix_path = Path("experiments/pipeline_v4/runs/v4_1_1/k200/EXPLORE_MATRIX.csv")
    matrix_data = {}
    with open(matrix_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = row['label']
            matrix_data[label] = row
    
    print(f"Loaded {len(queue)} candidates from promotion queue")
    
    # Apply hard filters
    filtered = []
    for candidate in queue:
        # Get corresponding matrix row
        label_base = candidate['label'].replace('_B', '')  # Remove arm suffix
        if label_base not in matrix_data:
            print(f"Warning: {label_base} not found in EXPLORE_MATRIX")
            continue
        
        matrix_row = matrix_data[label_base]
        
        # Hard filter 1: leakage_diff must be 0.000
        if candidate['leakage_diff'] != 0.0:
            continue
        
        # Hard filter 2: orbit must be isolated
        if not candidate['orbit']['is_isolated']:
            continue
        
        # Hard filter 3: Holm p-values must be < 0.01
        if (candidate['holm']['coverage']['p_holm'] >= 0.01 or
            candidate['holm']['f_words']['p_holm'] >= 0.01):
            continue
        
        # Passed all filters
        filtered.append((candidate, matrix_row))
    
    print(f"After hard filters: {len(filtered)} candidates remain")
    
    if not filtered:
        print("ERROR: No candidates passed hard filters!")
        return
    
    # Compute ranking keys and sort
    ranked = []
    for candidate, matrix_row in filtered:
        key = compute_ranking_key(candidate, matrix_row)
        ranked.append((key, candidate, matrix_row))
    
    # Sort by key (lexicographic, max-to-min for all positive components)
    ranked.sort(reverse=True)
    
    # Select top candidate
    winning_key, winner, winner_matrix = ranked[0]
    
    # Prepare selection record
    selection = {
        "selected_candidate": winner,
        "ranking_key": {
            "k1_window_robust_delta": winning_key[0],
            "k2_shuffled_margin": winning_key[1],
            "k3_coverage": winning_key[2],
            "k4_statistical_strength": winning_key[3],
            "k5_orbit_isolation": winning_key[4],
            "k6_verb_robustness": winning_key[5],
            "k7_function_words": winning_key[6],
            "k8_seed_tiebreaker": winning_key[7]
        },
        "matrix_metrics": {
            "fw_post": int(winner_matrix['fw_post']),
            "verb_post": int(winner_matrix['verb_post']),
            "cov_post": float(winner_matrix['cov_post']),
            "delta_windowed_min": float(winner_matrix['delta_windowed_min']),
            "delta_shuffled": float(winner_matrix['delta_shuffled'])
        },
        "total_candidates_evaluated": len(queue),
        "candidates_after_filters": len(filtered),
        "selection_reason": "Top ranked by 8-part lexicographic key"
    }
    
    # Save selection
    selection_path = Path("experiments/pipeline_v4/runs/v4_1_1/k200/CONFIRM_SELECTION.json")
    with open(selection_path, 'w') as f:
        json.dump(selection, f, indent=2)
    
    print(f"\n✅ Selected: {winner['label']}")
    print(f"   Seed: {winner['seed_u64']}")
    print(f"   Ranking key: {winning_key}")
    print(f"   Saved to: {selection_path}")
    
    # Also print the bundle path for next steps
    print(f"\n📦 Bundle directory: {winner['bundle_dir']}")
    
    # Show top 5 for transparency
    print(f"\nTop 5 candidates by ranking:")
    for i, (key, cand, _) in enumerate(ranked[:5]):
        print(f"  {i+1}. {cand['label']} - key: {key[:3]}...")  # Show first 3 components


if __name__ == "__main__":
    main()