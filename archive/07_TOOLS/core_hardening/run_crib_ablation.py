#!/usr/bin/env python3
"""
Crib Capacity Ablation Study
Tests wheel solving with subsets of anchor cells removed.
"""

import sys
import json
import csv
import time
import random
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from itertools import combinations

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))
from core_hardening_utils import *


def get_anchor_cells(anchors: Dict) -> List[int]:
    """Get list of all anchor cell indices."""
    cells = []
    for name, info in anchors.items():
        for i in range(info['start'], info['end'] + 1):
            cells.append(i)
    return sorted(cells)


def remove_cells(anchor_pt: Dict[int, str], cells_to_remove: List[int]) -> Dict[int, str]:
    """Remove specified cells from anchor constraints."""
    result = anchor_pt.copy()
    for cell in cells_to_remove:
        if cell in result:
            del result[cell]
    return result


def test_ablation(
    run_id: int,
    removed_cells: List[int],
    ct: str,
    full_anchor_pt: Dict[int, str]
) -> Dict:
    """Test wheel solving with specified cells removed."""
    
    # Remove cells from constraints
    constrained_pt = remove_cells(full_anchor_pt, removed_cells)
    
    # Group indices by baseline class
    class_indices = {c: [] for c in range(6)}
    for i in range(97):
        class_id = compute_baseline_class(i)
        class_indices[class_id].append(i)
    
    # Try to solve wheels
    wheels = {}
    for class_id in range(6):
        indices = class_indices[class_id]
        
        # Get remaining constraints for this class
        class_constraints = {i: constrained_pt[i] for i in indices if i in constrained_pt}
        
        if not class_constraints:
            # No constraints in this class
            return {
                'run_id': run_id,
                'removed_cells_json': json.dumps(removed_cells),
                'num_removed': len(removed_cells),
                'feasible': False,
                'reason': f'no_constraints_class_{class_id}',
                'pt_sha256': ''
            }
        
        # Try to solve wheel
        wheel_config = solve_class_wheel(
            class_id,
            indices,
            ct,
            class_constraints,
            enforce_option_a=True
        )
        
        if wheel_config is None:
            return {
                'run_id': run_id,
                'removed_cells_json': json.dumps(removed_cells),
                'num_removed': len(removed_cells),
                'feasible': False,
                'reason': f'solve_failed_class_{class_id}',
                'pt_sha256': ''
            }
        
        wheels[class_id] = wheel_config
    
    # Try to derive full plaintext
    try:
        derived_pt = derive_plaintext_from_wheels(ct, wheels, compute_baseline_class)
        
        if '?' in derived_pt:
            return {
                'run_id': run_id,
                'removed_cells_json': json.dumps(removed_cells),
                'num_removed': len(removed_cells),
                'feasible': False,
                'reason': 'incomplete_derivation',
                'pt_sha256': ''
            }
        
        pt_sha = compute_sha256(derived_pt)
        winner_sha = "4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79"
        
        return {
            'run_id': run_id,
            'removed_cells_json': json.dumps(removed_cells),
            'num_removed': len(removed_cells),
            'feasible': pt_sha == winner_sha,
            'reason': 'success' if pt_sha == winner_sha else 'wrong_plaintext',
            'pt_sha256': pt_sha
        }
        
    except Exception as e:
        return {
            'run_id': run_id,
            'removed_cells_json': json.dumps(removed_cells),
            'num_removed': len(removed_cells),
            'feasible': False,
            'reason': f'error:{str(e)[:30]}',
            'pt_sha256': ''
        }


def main():
    """Main crib ablation study."""
    parser = argparse.ArgumentParser(description='Crib capacity ablation study')
    parser.add_argument('--ct', default='02_DATA/ciphertext_97.txt')
    parser.add_argument('--anchors', default='02_DATA/anchors/four_anchors.json')
    parser.add_argument('--class-formula', default='baseline')
    parser.add_argument('--out', default='04_EXPERIMENTS/core_hardening_v2/crib_capacity')
    parser.add_argument('--master-seed', type=int, default=1337)
    args = parser.parse_args()
    
    print("Starting Crib Capacity Ablation Study")
    start_time = time.time()
    
    # Setup output directory
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Load ciphertext
    with open(args.ct, 'r') as f:
        ct = f.read().strip()
    
    # Load anchors
    with open(args.anchors, 'r') as f:
        anchors = json.load(f)
    
    # Get all anchor cells
    anchor_cells = get_anchor_cells(anchors)
    total_anchor_cells = len(anchor_cells)
    print(f"Total anchor cells: {total_anchor_cells}")
    
    # Build full anchor plaintext map
    full_anchor_pt = {}
    for name, info in anchors.items():
        for i in range(info['start'], info['end'] + 1):
            idx = i - info['start']
            if idx < len(info['plaintext']):
                full_anchor_pt[i] = info['plaintext'][idx]
    
    # Prepare CSV
    csv_path = out_dir / "ABLATION_MATRIX.csv"
    csv_file = open(csv_path, 'w', newline='')
    fieldnames = ['run_id', 'removed_cells_json', 'num_removed', 'feasible', 'reason', 'pt_sha256']
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()
    
    results = []
    run_id = 0
    
    # Test with no cells removed (baseline)
    print(f"Testing with 0 cells removed...")
    result = test_ablation(run_id, [], ct, full_anchor_pt)
    results.append(result)
    csv_writer.writerow(result)
    csv_file.flush()
    run_id += 1
    
    # Test removing k cells for various k values
    random.seed(args.master_seed)
    
    for k in [1, 2, 3, 4, 5, 10, 15, 20]:
        if k > total_anchor_cells:
            break
        
        print(f"Testing with {k} cells removed...")
        
        # Sample some combinations deterministically
        num_samples = min(10, len(list(combinations(range(total_anchor_cells), k))))
        
        if num_samples > 10:
            # Sample randomly but deterministically
            all_combos = list(combinations(anchor_cells, k))
            random.shuffle(all_combos)
            sampled_combos = all_combos[:10]
        else:
            sampled_combos = list(combinations(anchor_cells, k))[:num_samples]
        
        for combo in sampled_combos:
            result = test_ablation(run_id, list(combo), ct, full_anchor_pt)
            results.append(result)
            csv_writer.writerow(result)
            csv_file.flush()
            run_id += 1
    
    csv_file.close()
    
    # Create summary
    summary = {
        "total_runs": len(results),
        "feasible_count": sum(1 for r in results if r['feasible']),
        "by_num_removed": {}
    }
    
    for k in range(21):
        k_results = [r for r in results if r['num_removed'] == k]
        if k_results:
            summary["by_num_removed"][k] = {
                "tested": len(k_results),
                "feasible": sum(1 for r in k_results if r['feasible'])
            }
    
    summary_path = out_dir / "ABLATION_SUMMARY.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Generate manifest
    generate_manifest(out_dir)
    
    print(f"\nAblation study complete!")
    print(f"Total runs: {len(results)}")
    print(f"Feasible: {summary['feasible_count']}")
    print(f"Output: {out_dir}")


if __name__ == "__main__":
    main()