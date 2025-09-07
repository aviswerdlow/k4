#!/usr/bin/env python3
"""
Map schedule orbits to check for uniqueness.
Explores local equivalence classes via swaps and conjugates.
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Set
import sys
import copy

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from experiments.pipeline_v2.scripts.explore.run_anchor_modes import explore_score

def generate_single_swaps(sequence: List[int], anchor_positions: Set[int]) -> List[List[int]]:
    """
    Generate all single adjacent swaps that don't affect anchor positions.
    """
    neighbors = []
    
    for i in range(len(sequence) - 1):
        # Don't swap if either position is an anchor
        if i in anchor_positions or (i + 1) in anchor_positions:
            continue
            
        # Create swapped version
        swapped = sequence.copy()
        swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
        neighbors.append(swapped)
    
    return neighbors

def generate_double_swaps(sequence: List[int], anchor_positions: Set[int]) -> List[List[int]]:
    """
    Generate all double adjacent swaps (two disjoint pairs).
    """
    neighbors = []
    n = len(sequence)
    
    for i in range(n - 1):
        if i in anchor_positions or (i + 1) in anchor_positions:
            continue
            
        for j in range(i + 2, n - 1):
            if j in anchor_positions or (j + 1) in anchor_positions:
                continue
                
            # Create double-swapped version
            swapped = sequence.copy()
            swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
            swapped[j], swapped[j + 1] = swapped[j + 1], swapped[j]
            neighbors.append(swapped)
    
    return neighbors

def generate_grid_conjugates(route: Dict, anchor_positions: Set[int]) -> List[Dict]:
    """
    Generate conjugate permutations within grid family that preserve anchor positions.
    For grids, this includes row/column relabelings that fix anchor cells.
    """
    conjugates = []
    
    # Simplified conjugate generation
    # In production, would implement proper group-theoretic conjugates
    
    route_type = route.get("type", "")
    if "GRID" not in route_type:
        return conjugates
    
    # Example: transpose if it preserves anchors
    # (Would need actual grid structure to implement properly)
    
    return conjugates

def apply_permutation(text: str, permutation: List[int]) -> str:
    """
    Apply a permutation to text.
    """
    if len(permutation) != len(text):
        return text
    
    result = [''] * len(text)
    for i, pos in enumerate(permutation):
        if pos < len(text):
            result[i] = text[pos]
    
    return ''.join(result)

def map_orbit(plaintext: str, route: Dict, policy: Dict, output_dir: Path) -> Dict:
    """
    Map the orbit (equivalence class) of a candidate.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get anchor positions
    anchor_positions = set()
    for anchor, span in policy.get("anchor_config", {}).get("anchors", {}).items():
        if "span" in span:
            start, end = span["span"]
            anchor_positions.update(range(start, end + 1))
    
    # Create base permutation (identity for now)
    base_perm = list(range(len(plaintext)))
    
    # Generate neighbors
    print("Generating orbit neighbors...")
    
    single_swaps = generate_single_swaps(base_perm, anchor_positions)
    double_swaps = generate_double_swaps(base_perm, anchor_positions)
    conjugates = generate_grid_conjugates(route, anchor_positions)
    
    print(f"  Single swaps: {len(single_swaps)}")
    print(f"  Double swaps: {len(double_swaps)}")
    print(f"  Conjugates: {len(conjugates)}")
    
    # Score original
    original_score = explore_score(plaintext, policy, blinded=True)
    
    # Score neighbors
    results = []
    
    for swap_type, swaps in [("single", single_swaps), 
                             ("double", double_swaps)]:
        for i, perm in enumerate(swaps):
            # Apply permutation
            neighbor_text = apply_permutation(plaintext, perm)
            
            # Score neighbor
            neighbor_score = explore_score(neighbor_text, policy, blinded=True)
            
            # Compute delta
            delta = neighbor_score["final_score"] - original_score["final_score"]
            
            result = {
                "neighbor_type": swap_type,
                "neighbor_id": f"{swap_type}_{i}",
                "original_score": original_score["final_score"],
                "neighbor_score": neighbor_score["final_score"],
                "delta_score": delta,
                "delta_coverage": neighbor_score["coverage_score"] - original_score["coverage_score"],
                "within_tie": abs(delta) <= policy.get("orbit_epsilon", 0.02)
            }
            results.append(result)
    
    # Check uniqueness
    epsilon = policy.get("orbit_epsilon", 0.02)
    tie_threshold = policy.get("orbit_tie_threshold", 5)
    
    ties = [r for r in results if r["within_tie"]]
    unique = len(ties) < tie_threshold
    
    summary = {
        "plaintext_hash": hash(plaintext) % (10**8),
        "total_neighbors": len(results),
        "ties_within_epsilon": len(ties),
        "epsilon": epsilon,
        "tie_threshold": tie_threshold,
        "unique": unique,
        "original_score": original_score["final_score"]
    }
    
    # Write results
    csv_path = output_dir / "ORBIT_SUMMARY.csv"
    with open(csv_path, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    json_path = output_dir / "orbit_analysis.json"
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nOrbit analysis complete:")
    print(f"  Neighbors examined: {len(results)}")
    print(f"  Ties within ε={epsilon}: {len(ties)}")
    print(f"  Unique (ties < {tie_threshold}): {unique}")
    
    return summary

def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Map schedule orbits")
    parser.add_argument("--plaintext", default="WECANSEETHETEXTISCODEEASTNORTHEASTWESETTHECOURSETRUEREADTHENSEEBERLINCLOCKTHEJOYOFANANGLEISTHEARC")
    parser.add_argument("--route", default='{"type": "GRID_W14_ROWS"}')
    parser.add_argument("--policy", default="experiments/pipeline_v2/policies/explore/POLICY.orbits.json")
    parser.add_argument("--output", default="experiments/pipeline_v2/runs/2025-01-05/explore/orbits/test/")
    
    args = parser.parse_args()
    
    # Create orbit policy if needed
    if not Path(args.policy).exists():
        print(f"Creating orbit policy: {args.policy}")
        policy = {
            "name": "orbit_mapping",
            "orbit_epsilon": 0.02,
            "orbit_tie_threshold": 5,
            "anchor_config": {
                "anchors": {
                    "EAST": {"span": [21, 24]},
                    "NORTHEAST": {"span": [25, 33]},
                    "BERLINCLOCK": {"span": [63, 73]}
                }
            },
            "scorer": {
                "ngram_weight": 0.4,
                "coverage_weight": 0.3,
                "compress_weight": 0.3,
                "blind_anchors": True,
                "blind_narrative": True
            }
        }
        Path(args.policy).parent.mkdir(parents=True, exist_ok=True)
        with open(args.policy, 'w') as f:
            json.dump(policy, f, indent=2)
    
    # Load policy
    with open(args.policy) as f:
        policy = json.load(f)
    
    # Parse route
    if args.route.startswith('{'):
        route = json.loads(args.route)
    else:
        route = {"type": args.route}
    
    # Run orbit mapping
    map_orbit(args.plaintext, route, policy, Path(args.output))

if __name__ == "__main__":
    main()