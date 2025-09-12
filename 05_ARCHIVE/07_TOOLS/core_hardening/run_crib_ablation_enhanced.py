#!/usr/bin/env python3
"""
Enhanced Crib Capacity Ablation Study
Tests wheel solving with subsets of anchor cells removed.
Tracks undetermined positions and generates comprehensive coverage reports.
"""

import sys
import json
import csv
import time
import random
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
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


def analyze_coverage(
    ct: str,
    wheels: Dict[int, Dict],
    class_indices: Dict[int, List[int]]
) -> Tuple[List[int], Dict[int, List[int]], int]:
    """
    Analyze which positions are undetermined given wheel configurations.
    
    Returns:
        undetermined_indices: List of plaintext indices that cannot be derived
        missing_slots_per_class: Dict of class_id -> list of unconstrained slots
        undetermined_count: Total count of undetermined positions
    """
    undetermined_indices = []
    missing_slots_per_class = {}
    
    for i in range(len(ct)):
        class_id = compute_baseline_class(i)
        
        if class_id not in wheels:
            undetermined_indices.append(i)
            continue
            
        config = wheels[class_id]
        L = config['L']
        phase = config['phase']
        residues = config['residues']
        
        slot = (i - phase) % L
        if residues[slot] is None:
            undetermined_indices.append(i)
            if class_id not in missing_slots_per_class:
                missing_slots_per_class[class_id] = []
            if slot not in missing_slots_per_class[class_id]:
                missing_slots_per_class[class_id].append(slot)
    
    return undetermined_indices, missing_slots_per_class, len(undetermined_indices)


def test_ablation_with_coverage(
    run_id: int,
    removed_cells: List[int],
    ct: str,
    full_anchor_pt: Dict[int, str],
    constraints_used: str = "anchors_only"
) -> Tuple[Dict, Dict]:
    """
    Test wheel solving with coverage analysis.
    
    Returns:
        ablation_result: Standard ablation result dict
        coverage_result: Coverage analysis dict
    """
    
    # Remove cells from constraints
    constrained_pt = remove_cells(full_anchor_pt, removed_cells)
    
    # Group indices by baseline class
    class_indices = {c: [] for c in range(6)}
    for i in range(97):
        class_id = compute_baseline_class(i)
        class_indices[class_id].append(i)
    
    # Try to solve wheels
    wheels = {}
    classes_json = {}
    for class_id in range(6):
        indices = class_indices[class_id]
        classes_json[str(class_id)] = len(indices)
        
        # Get remaining constraints for this class
        class_constraints = {i: constrained_pt[i] for i in indices if i in constrained_pt}
        
        if not class_constraints:
            # No constraints in this class
            undetermined_indices = list(range(97))
            ablation_result = {
                'run_id': run_id,
                'removed_cells_json': json.dumps(removed_cells),
                'num_removed': len(removed_cells),
                'constraints_used': constraints_used,
                'undetermined_count': 97,
                'feasible': False,
                'reason': f'no_constraints_class_{class_id}',
                'pt_sha256': ''
            }
            coverage_result = {
                'run_id': run_id,
                'constraints_used': constraints_used,
                'classes_json': json.dumps(classes_json),
                'undetermined_indices_json': json.dumps(undetermined_indices),
                'undetermined_count': 97,
                'per_class_missing_slots_json': json.dumps({})
            }
            return ablation_result, coverage_result
        
        # Try to solve wheel
        wheel_config = solve_class_wheel(
            class_id,
            indices,
            ct,
            class_constraints,
            enforce_option_a=True
        )
        
        if wheel_config is None:
            undetermined_indices = [i for i in indices]
            ablation_result = {
                'run_id': run_id,
                'removed_cells_json': json.dumps(removed_cells),
                'num_removed': len(removed_cells),
                'constraints_used': constraints_used,
                'undetermined_count': len(indices),
                'feasible': False,
                'reason': f'solve_failed_class_{class_id}',
                'pt_sha256': ''
            }
            coverage_result = {
                'run_id': run_id,
                'constraints_used': constraints_used,
                'classes_json': json.dumps(classes_json),
                'undetermined_indices_json': json.dumps(undetermined_indices),
                'undetermined_count': len(indices),
                'per_class_missing_slots_json': json.dumps({})
            }
            return ablation_result, coverage_result
        
        wheels[class_id] = wheel_config
    
    # Analyze coverage
    undetermined_indices, missing_slots, undetermined_count = analyze_coverage(ct, wheels, class_indices)
    
    # Try to derive full plaintext
    try:
        derived_pt = derive_plaintext_from_wheels(ct, wheels, compute_baseline_class)
        
        if '?' in derived_pt:
            ablation_result = {
                'run_id': run_id,
                'removed_cells_json': json.dumps(removed_cells),
                'num_removed': len(removed_cells),
                'constraints_used': constraints_used,
                'undetermined_count': undetermined_count,
                'feasible': False,
                'reason': 'incomplete_derivation',
                'pt_sha256': ''
            }
        else:
            pt_sha = compute_sha256(derived_pt)
            winner_sha = "4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79"
            
            ablation_result = {
                'run_id': run_id,
                'removed_cells_json': json.dumps(removed_cells),
                'num_removed': len(removed_cells),
                'constraints_used': constraints_used,
                'undetermined_count': undetermined_count,
                'feasible': pt_sha == winner_sha,
                'reason': 'success' if pt_sha == winner_sha else 'wrong_plaintext',
                'pt_sha256': pt_sha if pt_sha == winner_sha else ''
            }
        
        coverage_result = {
            'run_id': run_id,
            'constraints_used': constraints_used,
            'classes_json': json.dumps(classes_json),
            'undetermined_indices_json': json.dumps(undetermined_indices),
            'undetermined_count': undetermined_count,
            'per_class_missing_slots_json': json.dumps({k: v for k, v in missing_slots.items()})
        }
        
        return ablation_result, coverage_result
        
    except Exception as e:
        ablation_result = {
            'run_id': run_id,
            'removed_cells_json': json.dumps(removed_cells),
            'num_removed': len(removed_cells),
            'constraints_used': constraints_used,
            'undetermined_count': -1,
            'feasible': False,
            'reason': f'error:{str(e)[:30]}',
            'pt_sha256': ''
        }
        coverage_result = {
            'run_id': run_id,
            'constraints_used': constraints_used,
            'classes_json': json.dumps(classes_json),
            'undetermined_indices_json': json.dumps([]),
            'undetermined_count': -1,
            'per_class_missing_slots_json': json.dumps({})
        }
        return ablation_result, coverage_result


def run_control_test(ct: str, pt: str) -> Dict:
    """
    Run control test with full constraints (anchors + tail).
    """
    # Use full plaintext as constraints
    pt_constraints = {i: pt[i] for i in range(97)}
    
    # Group indices by baseline class
    class_indices = {c: [] for c in range(6)}
    for i in range(97):
        class_id = compute_baseline_class(i)
        class_indices[class_id].append(i)
    
    # Solve all wheels
    wheels = {}
    for class_id in range(6):
        indices = class_indices[class_id]
        class_constraints = {i: pt_constraints[i] for i in indices}
        
        wheel_config = solve_class_wheel(
            class_id,
            indices,
            ct,
            class_constraints,
            enforce_option_a=True
        )
        
        if wheel_config is None:
            return {
                'constraints_used': 'anchors_plus_tail',
                'feasible': False,
                'reason': f'solve_failed_class_{class_id}',
                'pt_sha256': '',
                'undetermined_count': -1
            }
        
        wheels[class_id] = wheel_config
    
    # Derive plaintext
    derived_pt = derive_plaintext_from_wheels(ct, wheels, compute_baseline_class)
    undetermined_count = derived_pt.count('?')
    
    if undetermined_count > 0:
        return {
            'constraints_used': 'anchors_plus_tail',
            'feasible': False,
            'reason': 'incomplete_derivation',
            'pt_sha256': '',
            'undetermined_count': undetermined_count
        }
    
    pt_sha = compute_sha256(derived_pt)
    winner_sha = "4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79"
    
    return {
        'constraints_used': 'anchors_plus_tail',
        'feasible': pt_sha == winner_sha,
        'reason': 'success' if pt_sha == winner_sha else 'wrong_plaintext',
        'pt_sha256': pt_sha,
        'undetermined_count': 0
    }


def main():
    """Main enhanced crib ablation study."""
    parser = argparse.ArgumentParser(description='Enhanced crib capacity ablation study')
    parser.add_argument('--ct', default='02_DATA/ciphertext_97.txt')
    parser.add_argument('--pt', default='01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt')
    parser.add_argument('--anchors', default='02_DATA/anchors/four_anchors.json')
    parser.add_argument('--class-formula', default='baseline')
    parser.add_argument('--out', default='04_EXPERIMENTS/core_hardening_v2/crib_capacity')
    parser.add_argument('--master-seed', type=int, default=1337)
    args = parser.parse_args()
    
    print("Starting Enhanced Crib Capacity Ablation Study")
    start_time = time.time()
    
    # Setup output directory
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Load ciphertext and plaintext
    with open(args.ct, 'r') as f:
        ct = f.read().strip()
    
    with open(args.pt, 'r') as f:
        pt = f.read().strip()
    
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
    
    # Prepare CSV files
    ablation_csv_path = out_dir / "ABLATION_MATRIX.csv"
    coverage_csv_path = out_dir / "ABLATION_COVERAGE.csv"
    control_csv_path = out_dir / "ABLATION_CONTROL.csv"
    
    # Ablation matrix
    ablation_file = open(ablation_csv_path, 'w', newline='')
    ablation_fieldnames = ['run_id', 'removed_cells_json', 'num_removed', 'constraints_used', 
                          'undetermined_count', 'feasible', 'reason', 'pt_sha256']
    ablation_writer = csv.DictWriter(ablation_file, fieldnames=ablation_fieldnames)
    ablation_writer.writeheader()
    
    # Coverage matrix
    coverage_file = open(coverage_csv_path, 'w', newline='')
    coverage_fieldnames = ['run_id', 'constraints_used', 'classes_json', 
                          'undetermined_indices_json', 'undetermined_count', 
                          'per_class_missing_slots_json']
    coverage_writer = csv.DictWriter(coverage_file, fieldnames=coverage_fieldnames)
    coverage_writer.writeheader()
    
    results = []
    coverage_results = []
    run_id = 0
    baseline_undetermined_indices = None
    baseline_missing_slots = None
    
    # Test with no cells removed (baseline)
    print(f"Testing with 0 cells removed...")
    ablation_result, coverage_result = test_ablation_with_coverage(
        run_id, [], ct, full_anchor_pt, "anchors_only"
    )
    results.append(ablation_result)
    coverage_results.append(coverage_result)
    ablation_writer.writerow(ablation_result)
    coverage_writer.writerow(coverage_result)
    ablation_file.flush()
    coverage_file.flush()
    
    # Save baseline undetermined indices
    if run_id == 0:
        baseline_undetermined_indices = json.loads(coverage_result['undetermined_indices_json'])
        baseline_missing_slots = json.loads(coverage_result['per_class_missing_slots_json'])
    
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
            ablation_result, coverage_result = test_ablation_with_coverage(
                run_id, list(combo), ct, full_anchor_pt, "anchors_only"
            )
            results.append(ablation_result)
            coverage_results.append(coverage_result)
            ablation_writer.writerow(ablation_result)
            coverage_writer.writerow(coverage_result)
            ablation_file.flush()
            coverage_file.flush()
            run_id += 1
    
    ablation_file.close()
    coverage_file.close()
    
    # Run control test with anchors + tail
    print("Running control test with anchors + tail...")
    control_result = run_control_test(ct, pt)
    
    control_file = open(control_csv_path, 'w', newline='')
    control_fieldnames = ['constraints_used', 'feasible', 'reason', 'pt_sha256', 'undetermined_count']
    control_writer = csv.DictWriter(control_file, fieldnames=control_fieldnames)
    control_writer.writeheader()
    control_writer.writerow(control_result)
    control_file.close()
    
    # Create metadata JSON
    metadata = {
        "seed": args.master_seed,
        "invariants": {
            "optionA": True,
            "no_tail_guard": True,
            "anchors": {
                "EAST": [21, 24],
                "NORTHEAST": [25, 33],
                "BERLIN": [63, 68],
                "CLOCK": [69, 73]
            }
        },
        "constraints_used": "anchors_only",
        "runs": len(results),
        "date_utc": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "commit": "HEAD"  # Would need git integration for real commit
    }
    
    metadata_path = out_dir / "ABLATION_MATRIX.meta.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Create undetermined indices JSON for baseline
    if baseline_undetermined_indices is not None:
        undetermined_json = {
            "constraints_used": "anchors_only",
            "undetermined_indices": baseline_undetermined_indices,
            "per_class_missing": baseline_missing_slots,
            "note": "Indices that are not derivable with anchors-only; explains why anchors-only feasible=0 even with k=0."
        }
        
        undetermined_path = out_dir / "UNDETERMINED_INDICES.json"
        with open(undetermined_path, 'w') as f:
            json.dump(undetermined_json, f, indent=2)
    
    # Create summary
    summary = {
        "seed": args.master_seed,
        "constraints_used": "anchors_only",
        "runs": len(results),
        "feasible": sum(1 for r in results if r['feasible']),
        "incomplete_derivation_runs": sum(1 for r in results if r['reason'] == 'incomplete_derivation'),
        "baseline_undetermined_count": results[0]['undetermined_count'] if results else 0,
        "control": {
            "constraints_used": control_result['constraints_used'],
            "feasible": control_result['feasible'],
            "pt_sha256": control_result['pt_sha256'],
            "undetermined_count": control_result['undetermined_count']
        }
    }
    
    summary_path = out_dir / "ABLATION_SUMMARY.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Generate manifest
    generate_manifest(out_dir)
    
    print(f"\nEnhanced ablation study complete!")
    print(f"Total runs: {len(results)}")
    print(f"Feasible (anchors-only): {summary['feasible']}")
    print(f"Baseline undetermined: {summary['baseline_undetermined_count']} positions")
    print(f"Control feasible: {control_result['feasible']}")
    print(f"Output: {out_dir}")


if __name__ == "__main__":
    main()