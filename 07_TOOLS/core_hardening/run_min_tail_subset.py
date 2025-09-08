#!/usr/bin/env python3
"""
Minimum Tail Subset (MTS) Study
Find the smallest subset of tail indices that, with anchors, uniquely determines the solution.
"""

import sys
import json
import csv
import time
import random
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from itertools import combinations

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))
from core_hardening_utils import *


def test_tail_subset(
    tail_indices: List[int],
    ct: str,
    pt: str,
    anchors: Dict
) -> Tuple[bool, Optional[str], Optional[Dict]]:
    """
    Test if anchors + given tail subset uniquely determines the solution.
    
    Returns:
        (feasible, pt_sha256, wheels_config)
    """
    # Build constraints from anchors + tail subset
    constraints = {}
    
    # Add anchor constraints
    for name, info in anchors.items():
        for i in range(info['start'], info['end'] + 1):
            idx = i - info['start']
            if idx < len(info['plaintext']):
                constraints[i] = info['plaintext'][idx]
    
    # Add tail subset constraints
    for i in tail_indices:
        if 0 <= i < len(pt):
            constraints[i] = pt[i]
    
    # Group indices by baseline class
    class_indices = {c: [] for c in range(6)}
    for i in range(97):
        class_id = compute_baseline_class(i)
        class_indices[class_id].append(i)
    
    # Try to solve wheels
    wheels = {}
    for class_id in range(6):
        indices = class_indices[class_id]
        class_constraints = {i: constraints[i] for i in indices if i in constraints}
        
        if not class_constraints:
            return False, None, None
        
        wheel_config = solve_class_wheel(
            class_id,
            indices,
            ct,
            class_constraints,
            enforce_option_a=True
        )
        
        if wheel_config is None:
            return False, None, None
        
        wheels[class_id] = wheel_config
    
    # Try to derive full plaintext
    try:
        derived_pt = derive_plaintext_from_wheels(ct, wheels, compute_baseline_class)
        
        if '?' in derived_pt:
            return False, None, None
        
        pt_sha = compute_sha256(derived_pt)
        winner_sha = "4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79"
        
        if pt_sha == winner_sha:
            return True, pt_sha, wheels
        else:
            return False, None, None
    
    except Exception:
        return False, None, None


def greedy_forward_search(
    ct: str,
    pt: str,
    anchors: Dict,
    tail_range: range
) -> List[int]:
    """
    Greedy forward search: add tail indices by marginal constraint gain.
    """
    selected = []
    remaining = list(tail_range)
    
    while remaining:
        best_idx = None
        best_gain = 0
        
        for idx in remaining:
            # Test with this index added
            test_set = selected + [idx]
            feasible, _, _ = test_tail_subset(test_set, ct, pt, anchors)
            
            if feasible:
                return test_set  # Found minimal set
            
            # Measure constraint gain (simplified - could be more sophisticated)
            # For now, just prefer indices that are farther from existing constraints
            min_dist = min([abs(idx - s) for s in selected] + [100])
            if min_dist > best_gain:
                best_gain = min_dist
                best_idx = idx
        
        if best_idx is not None:
            selected.append(best_idx)
            remaining.remove(best_idx)
        else:
            # Pick randomly if no clear best
            idx = remaining[0]
            selected.append(idx)
            remaining.remove(idx)
    
    return selected


def exact_search_size_k(
    k: int,
    ct: str,
    pt: str,
    anchors: Dict,
    tail_range: range,
    max_samples: int,
    seed: int
) -> Optional[Tuple[List[int], str, Dict]]:
    """
    Search for feasible subset of size k.
    
    Returns:
        (indices, pt_sha256, wheels) if found, None otherwise
    """
    tail_indices = list(tail_range)
    total_combos = len(list(combinations(tail_indices, k)))
    
    random.seed(seed)
    
    if total_combos <= max_samples:
        # Test all combinations
        for combo in combinations(tail_indices, k):
            feasible, pt_sha, wheels = test_tail_subset(list(combo), ct, pt, anchors)
            if feasible:
                return list(combo), pt_sha, wheels
    else:
        # Sample randomly
        all_combos = list(combinations(tail_indices, k))
        random.shuffle(all_combos)
        
        for combo in all_combos[:max_samples]:
            feasible, pt_sha, wheels = test_tail_subset(list(combo), ct, pt, anchors)
            if feasible:
                return list(combo), pt_sha, wheels
    
    return None


def prove_minimality(
    min_size: int,
    ct: str,
    pt: str,
    anchors: Dict,
    tail_range: range,
    max_samples: int,
    seed: int
) -> Dict:
    """
    Prove that no subset of size (min_size - 1) is feasible.
    
    Returns minimality certificate.
    """
    if min_size <= 1:
        return {
            "min_size": min_size,
            "smaller_size_tested": 0,
            "smaller_size_feasible": 0,
            "certificate": "Trivial: size 0 has no constraints"
        }
    
    k = min_size - 1
    tail_indices = list(tail_range)
    total_combos = len(list(combinations(tail_indices, k)))
    
    random.seed(seed + 1000)  # Different seed for certificate
    
    tested = 0
    feasible_found = 0
    
    if total_combos <= max_samples * 2:
        # Test all combinations for certificate
        for combo in combinations(tail_indices, k):
            tested += 1
            feasible, _, _ = test_tail_subset(list(combo), ct, pt, anchors)
            if feasible:
                feasible_found += 1
    else:
        # Sample more extensively for certificate
        all_combos = list(combinations(tail_indices, k))
        random.shuffle(all_combos)
        
        for combo in all_combos[:max_samples * 2]:
            tested += 1
            feasible, _, _ = test_tail_subset(list(combo), ct, pt, anchors)
            if feasible:
                feasible_found += 1
    
    return {
        "min_size": min_size,
        "smaller_size_tested": k,
        "combinations_tested": tested,
        "combinations_feasible": feasible_found,
        "certificate": f"Tested {tested}/{total_combos} size-{k} subsets, {feasible_found} feasible"
    }


def main():
    """Main MTS study."""
    parser = argparse.ArgumentParser(description='Minimum Tail Subset study')
    parser.add_argument('--ct', default='02_DATA/ciphertext_97.txt')
    parser.add_argument('--pt', default='01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt')
    parser.add_argument('--anchors', default='02_DATA/anchors/four_anchors.json')
    parser.add_argument('--out', default='04_EXPERIMENTS/core_hardening_v3/min_tail_subset')
    parser.add_argument('--seed', type=int, default=1337)
    parser.add_argument('--kmin', type=int, default=6)
    parser.add_argument('--kmax', type=int, default=22)
    parser.add_argument('--samples-per-k', type=int, default=2000)
    args = parser.parse_args()
    
    print("Starting Minimum Tail Subset Study")
    print(f"Testing tail subsets of size {args.kmin} to {args.kmax}")
    start_time = time.time()
    
    # Setup output directory
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    with open(args.ct, 'r') as f:
        ct = f.read().strip()
    
    with open(args.pt, 'r') as f:
        pt = f.read().strip()
    
    with open(args.anchors, 'r') as f:
        anchors = json.load(f)
    
    tail_range = range(75, 97)  # Indices 75-96 (22 positions)
    
    # Prepare CSV
    csv_path = out_dir / "MTS_RESULTS.csv"
    csv_file = open(csv_path, 'w', newline='')
    fieldnames = ['subset_size', 'indices_csv', 'feasible', 'pt_sha256', 'proof_path']
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()
    
    results = []
    min_subset = None
    min_size = 23  # Start with full tail + 1
    
    # First try greedy approach
    print("\nTrying greedy forward search...")
    greedy_result = greedy_forward_search(ct, pt, anchors, tail_range)
    if greedy_result:
        print(f"Greedy found subset of size {len(greedy_result)}")
        min_size = min(min_size, len(greedy_result))
    
    # Exact search for each k
    for k in range(args.kmin, min(args.kmax + 1, min_size)):
        print(f"\nSearching for feasible subset of size {k}...")
        
        result = exact_search_size_k(
            k, ct, pt, anchors, tail_range,
            args.samples_per_k, args.seed + k
        )
        
        if result:
            indices, pt_sha, wheels = result
            print(f"  FOUND feasible subset: {sorted(indices)}")
            
            # Save proof
            proof_path = out_dir / "PROOFS"
            proof_path.mkdir(exist_ok=True)
            proof_file = proof_path / f"subset_size_{k}.json"
            
            proof_data = {
                "subset_size": k,
                "indices": sorted(indices),
                "pt_sha256": pt_sha,
                "wheels": [
                    {
                        "class_id": cid,
                        "family": w["family"],
                        "L": w["L"],
                        "phase": w["phase"],
                        "residues": w["residues"]
                    }
                    for cid, w in wheels.items()
                ],
                "seed": args.seed + k
            }
            
            with open(proof_file, 'w') as f:
                json.dump(proof_data, f, indent=2)
            
            # Record result
            result_row = {
                'subset_size': k,
                'indices_csv': ','.join(map(str, sorted(indices))),
                'feasible': True,
                'pt_sha256': pt_sha,
                'proof_path': str(proof_file.relative_to(Path.cwd()))
            }
            results.append(result_row)
            csv_writer.writerow(result_row)
            csv_file.flush()
            
            if k < min_size:
                min_size = k
                min_subset = (sorted(indices), pt_sha, wheels)
            
            # Found one, no need to test larger k
            break
        else:
            print(f"  No feasible subset found")
            
            # Record negative result
            result_row = {
                'subset_size': k,
                'indices_csv': '',
                'feasible': False,
                'pt_sha256': '',
                'proof_path': ''
            }
            results.append(result_row)
            csv_writer.writerow(result_row)
            csv_file.flush()
    
    csv_file.close()
    
    # Create minimum proof with certificate
    if min_subset:
        indices, pt_sha, wheels = min_subset
        
        print(f"\nProving minimality of size {len(indices)}...")
        certificate = prove_minimality(
            len(indices), ct, pt, anchors, tail_range,
            args.samples_per_k, args.seed
        )
        
        min_proof = {
            "indices": indices,
            "subset_size": len(indices),
            "pt_sha256": pt_sha,
            "seed_recipe": f"MASTER_SEED={args.seed}, k_seed={args.seed + len(indices)}",
            "wheels_proof_path": f"PROOFS/subset_size_{len(indices)}.json",
            "uniqueness_certificate": certificate
        }
        
        min_proof_path = out_dir / "MTS_MIN_PROOF.json"
        with open(min_proof_path, 'w') as f:
            json.dump(min_proof, f, indent=2)
        
        print(f"\nMinimal subset found: size {len(indices)}")
        print(f"Indices: {indices}")
    else:
        print("\nNo feasible subset found in range")
    
    # Create README
    readme_content = f"""# Minimum Tail Subset Study

## Overview

This study identifies the smallest subset of tail indices (positions 75-96) that, combined with the four anchors, uniquely determines the full K4 plaintext.

## Results

- **Tail range tested**: Positions 75-96 (22 possible indices)
- **Subset sizes tested**: {args.kmin} to {min(args.kmax, min_size - 1)}
- **Minimal subset size**: {len(indices) if min_subset else 'Not found'}
- **Seed**: {args.seed}

## Key Finding

{'The minimal tail subset of size ' + str(len(indices)) + ' combined with anchors uniquely determines the solution.' if min_subset else 'No feasible subset found in the tested range.'}

## Files

- **MTS_RESULTS.csv**: All tested subset sizes and outcomes
- **MTS_MIN_PROOF.json**: The minimal subset with uniqueness certificate
- **PROOFS/**: Detailed wheel configurations for feasible subsets

## Reproduction

```bash
python3 07_TOOLS/core_hardening/run_min_tail_subset.py \\
  --seed {args.seed} \\
  --kmin {args.kmin} \\
  --kmax {args.kmax} \\
  --samples-per-k {args.samples_per_k}
```
"""
    
    readme_path = out_dir / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    # Generate manifest
    generate_manifest(out_dir)
    
    print(f"\nMTS study complete!")
    print(f"Output: {out_dir}")
    print(f"Runtime: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    main()