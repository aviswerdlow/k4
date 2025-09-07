#!/usr/bin/env python3
"""Select next Confirm candidate after previous failure."""

import json
from pathlib import Path
from select_confirm_candidate import compute_ranking_key
import csv


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
    
    # Load rejection log to skip already tried candidates
    rejects_path = Path("runs/confirm/rejects.json")
    if rejects_path.exists():
        with open(rejects_path) as f:
            rejects = json.load(f)
    else:
        rejects = []
    
    rejected_labels = {r['label'] for r in rejects}
    
    print(f"Already rejected: {rejected_labels}")
    
    # Apply hard filters and skip rejected
    filtered = []
    for candidate in queue:
        if candidate['label'] in rejected_labels:
            continue
        
        # Get corresponding matrix row
        label_base = candidate['label'].replace('_B', '')
        if label_base not in matrix_data:
            continue
        
        matrix_row = matrix_data[label_base]
        
        # Hard filters
        if candidate['leakage_diff'] != 0.0:
            continue
        if not candidate['orbit']['is_isolated']:
            continue
        if (candidate['holm']['coverage']['p_holm'] >= 0.01 or
            candidate['holm']['f_words']['p_holm'] >= 0.01):
            continue
        
        filtered.append((candidate, matrix_row))
    
    print(f"After filters and exclusions: {len(filtered)} candidates remain")
    
    if not filtered:
        print("ERROR: No more candidates available!")
        return None
    
    # Compute ranking keys and sort
    ranked = []
    for candidate, matrix_row in filtered:
        key = compute_ranking_key(candidate, matrix_row)
        ranked.append((key, candidate, matrix_row))
    
    ranked.sort(reverse=True)
    
    # Select top remaining candidate
    winning_key, winner, winner_matrix = ranked[0]
    
    print(f"\n✅ Next candidate: {winner['label']}")
    print(f"   Seed: {winner['seed_u64']}")
    print(f"   Ranking key: {winning_key[:3]}...")
    
    # Update selection file
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
        "attempt_number": len(rejects) + 2,
        "previously_rejected": list(rejected_labels)
    }
    
    selection_path = Path("experiments/pipeline_v4/runs/v4_1_1/k200/CONFIRM_SELECTION.json")
    with open(selection_path, 'w') as f:
        json.dump(selection, f, indent=2)
    
    print(f"Updated: {selection_path}")
    
    # Show top 5 remaining
    print(f"\nTop 5 remaining candidates:")
    for i, (key, cand, _) in enumerate(ranked[:5]):
        print(f"  {i+1}. {cand['label']} - key: {key[:3]}...")
    
    return winner


if __name__ == "__main__":
    winner = main()
    if winner:
        print(f"\n📦 Ready to try: {winner['label']}")
    else:
        print("\n❌ No more candidates available - SATURATION")