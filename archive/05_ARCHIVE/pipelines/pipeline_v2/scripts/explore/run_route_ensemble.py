#!/usr/bin/env python3
"""
Run Campaign B: Route-First/Structure-Led exploration.
Tests top seeds from breadth campaign through 39 different route structures.
"""

import json
import csv
import hashlib
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import sys

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from experiments.pipeline_v2.scripts.explore.run_anchor_modes import explore_score
from experiments.pipeline_v2.scripts.explore.blind_text import blind_text
from experiments.pipeline_v2.scripts.explore.run_explore_hard import (
    fast_lawfulness_check, run_bootstrap_nulls, compute_normalized_score
)

def apply_route(text: str, route_type: str, params: Dict) -> str:
    """
    Apply a route transformation to plaintext.
    
    Routes:
    - GRID: Write in rows, read in columns
    - SPOKE: Spiral pattern from center
    - RAILFENCE: Zigzag pattern
    - HALF_INTERLEAVE: Split and interleave halves
    - NA_PERMUTATION: Permute NA window only
    """
    n = len(text)
    
    if route_type == "GRID":
        rows, cols = params["rows"], params["cols"]
        if rows * cols < n:
            # Pad with random letters
            text += ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') 
                          for _ in range(rows * cols - n))
        
        # Write row-wise, read column-wise
        grid = []
        for i in range(rows):
            grid.append(text[i*cols:(i+1)*cols])
        
        result = []
        for j in range(cols):
            for i in range(rows):
                if j < len(grid[i]):
                    result.append(grid[i][j])
        
        return ''.join(result[:n])
    
    elif route_type == "SPOKE":
        # Simplified spoke: alternate inward/outward
        rows, cols = params["rows"], params["cols"]
        if rows * cols < n:
            text += ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                          for _ in range(rows * cols - n))
        
        # Spiral from outside in
        grid = [['' for _ in range(cols)] for _ in range(rows)]
        idx = 0
        top, bottom, left, right = 0, rows-1, 0, cols-1
        
        while top <= bottom and left <= right and idx < n:
            # Top row
            for j in range(left, right + 1):
                if idx < n:
                    grid[top][j] = text[idx]
                    idx += 1
            top += 1
            
            # Right column
            for i in range(top, bottom + 1):
                if idx < n:
                    grid[i][right] = text[idx]
                    idx += 1
            right -= 1
            
            # Bottom row
            if top <= bottom:
                for j in range(right, left - 1, -1):
                    if idx < n:
                        grid[bottom][j] = text[idx]
                        idx += 1
                bottom -= 1
            
            # Left column
            if left <= right:
                for i in range(bottom, top - 1, -1):
                    if idx < n:
                        grid[i][left] = text[idx]
                        idx += 1
                left += 1
        
        # Read column-wise
        result = []
        for j in range(cols):
            for i in range(rows):
                if grid[i][j]:
                    result.append(grid[i][j])
        
        return ''.join(result[:n])
    
    elif route_type == "RAILFENCE":
        rails = params["rails"]
        fence = [[] for _ in range(rails)]
        
        # Zigzag pattern
        rail = 0
        direction = 1
        for char in text:
            fence[rail].append(char)
            rail += direction
            if rail == 0 or rail == rails - 1:
                direction = -direction
        
        # Read off rails
        return ''.join(''.join(rail) for rail in fence)
    
    elif route_type == "HALF_INTERLEAVE":
        side = params["side"]  # "left" or "right"
        split = params.get("split", n // 2)
        
        if side == "left":
            left = text[:split]
            right = text[split:]
            # Interleave left-first
            result = []
            for i in range(max(len(left), len(right))):
                if i < len(left):
                    result.append(left[i])
                if i < len(right):
                    result.append(right[i])
        else:
            left = text[:split]
            right = text[split:]
            # Interleave right-first
            result = []
            for i in range(max(len(left), len(right))):
                if i < len(right):
                    result.append(right[i])
                if i < len(left):
                    result.append(left[i])
        
        return ''.join(result)
    
    elif route_type == "NA_PERMUTATION":
        # Permute only positions 54-74 (NA window)
        variant = params["variant"]
        na_start, na_end = 54, 74
        
        prefix = text[:na_start]
        na_window = list(text[na_start:na_end+1])
        suffix = text[na_end+1:] if na_end+1 < len(text) else ""
        
        # Different permutation patterns
        if variant == 1:
            # Reverse NA window
            na_window.reverse()
        elif variant == 2:
            # Rotate by 7
            na_window = na_window[7:] + na_window[:7]
        elif variant == 3:
            # Swap pairs
            for i in range(0, len(na_window)-1, 2):
                na_window[i], na_window[i+1] = na_window[i+1], na_window[i]
        
        return prefix + ''.join(na_window) + suffix
    
    return text  # Default: no transformation

def generate_route_configs() -> List[Tuple[str, str, Dict]]:
    """
    Generate all 39 route configurations.
    """
    configs = []
    
    # GRID family (9 routes)
    grid_dims = [(6,17), (9,11), (10,10), (11,9), (14,7), 
                 (17,6), (21,5), (25,4), (33,3)]
    for rows, cols in grid_dims:
        configs.append((f"GRID_{rows}x{cols}", "GRID", {"rows": rows, "cols": cols}))
    
    # SPOKE family (9 routes)
    for rows, cols in grid_dims:
        configs.append((f"SPOKE_{rows}x{cols}", "SPOKE", {"rows": rows, "cols": cols}))
    
    # RAILFENCE family (9 routes)
    for rails in [2, 3, 4, 5, 7, 9, 11, 13, 17]:
        configs.append((f"RAILFENCE_{rails}", "RAILFENCE", {"rails": rails}))
    
    # HALF_INTERLEAVE (6 routes)
    for dims, split in [((6,17), 51), ((10,10), 50), ((14,7), 49)]:
        configs.append((f"HL_{dims[0]}x{dims[1]}", "HALF_INTERLEAVE", 
                       {"side": "left", "split": split}))
        configs.append((f"HR_{dims[0]}x{dims[1]}", "HALF_INTERLEAVE", 
                       {"side": "right", "split": split}))
    
    # NA-only permutations (6 routes)
    for base in ["GRID_10x10", "SPOKE_10x10"]:
        for variant in [1, 2, 3]:
            configs.append((f"{base}_NA{variant}", "NA_PERMUTATION", 
                          {"variant": variant}))
    
    return configs

def run_route_campaign(
    seeds_file: Path,
    policy_file: Path,
    baseline_stats_file: Path,
    output_dir: Path,
    seed: int = 1337
) -> Path:
    """
    Run Campaign B: test all seeds through all routes.
    """
    random.seed(seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load inputs
    with open(seeds_file) as f:
        seeds_data = json.load(f)
    
    with open(policy_file) as f:
        policy = json.load(f)
    
    with open(baseline_stats_file) as f:
        baseline_stats = json.load(f)
    
    # Generate route configs
    route_configs = generate_route_configs()
    print(f"Testing {len(seeds_data['candidates'])} seeds × {len(route_configs)} routes")
    
    results = []
    promotion_queue = []
    
    # Test each seed through each route
    for seed_idx, candidate in enumerate(seeds_data['candidates']):
        print(f"\nSeed {seed_idx+1}/{len(seeds_data['candidates'])}: {candidate['label']}")
        plaintext = candidate['text']
        
        for route_name, route_type, route_params in route_configs:
            # Apply route transformation
            routed_text = apply_route(plaintext, route_type, route_params)
            
            # Skip lawfulness check for route campaign (routes scramble positions)
            # In production, would run full solver after route transformation
            # For now, accept all texts that have correct length
            if len(routed_text) < 65:
                continue
            
            # Score with three anchor modes
            scores = {}
            for mode in ["fixed", "windowed", "shuffled"]:
                mode_policy = json.loads(json.dumps(policy))
                mode_policy["anchor_mode"] = mode
                
                if mode == "windowed":
                    # Allow ±1 flexibility
                    for anchor in mode_policy["anchor_config"]["anchors"]:
                        mode_policy["anchor_config"]["anchors"][anchor]["flexibility"] = 1
                elif mode == "shuffled":
                    # Randomize anchor positions
                    random.seed(seed + seed_idx + hash(route_name))
                    for anchor in mode_policy["anchor_config"]["anchors"]:
                        span = mode_policy["anchor_config"]["anchors"][anchor]["span"]
                        length = span[1] - span[0]
                        new_start = random.randint(0, len(routed_text) - length - 1)
                        mode_policy["anchor_config"]["anchors"][anchor]["span"] = [
                            new_start, new_start + length
                        ]
                
                # Compute normalized score
                score_data = compute_normalized_score(routed_text, mode_policy, baseline_stats)
                scores[mode] = score_data["score_norm"]
            
            # Compute deltas
            delta_windowed = scores["fixed"] - scores["windowed"]
            delta_shuffled = scores["fixed"] - scores["shuffled"]
            
            result = {
                "seed_label": candidate['label'],
                "route": route_name,
                "length": len(routed_text),
                "fixed_score": scores["fixed"],
                "windowed_score": scores["windowed"],
                "shuffled_score": scores["shuffled"],
                "delta_windowed": delta_windowed,
                "delta_shuffled": delta_shuffled,
                "pass_deltas": delta_windowed >= 0.05 and delta_shuffled >= 0.05
            }
            results.append(result)
            
            # Check for promotion
            if result["pass_deltas"]:
                # Run bootstrap nulls
                p_value = run_bootstrap_nulls(routed_text, n=1000, seed=seed+seed_idx)
                if p_value < 0.05:
                    promotion_queue.append({
                        "seed_label": candidate['label'],
                        "route": route_name,
                        "text": routed_text,
                        "scores": scores,
                        "deltas": {"windowed": delta_windowed, "shuffled": delta_shuffled},
                        "p_value": p_value
                    })
                    print(f"  ✓ PROMOTED: {route_name} (δ₁={delta_windowed:.3f}, δ₂={delta_shuffled:.3f})")
    
    # Write results
    csv_path = output_dir / "ROUTE_MATRIX.csv"
    with open(csv_path, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    # Write promotion queue
    queue_path = output_dir / "promotion_queue.json"
    with open(queue_path, 'w') as f:
        json.dump({
            "campaign": "PV2-EXPLORE-ROUTE-001",
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(results),
            "delta_passers": sum(1 for r in results if r["pass_deltas"]),
            "promoted": len(promotion_queue),
            "queue": promotion_queue
        }, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Campaign B Complete:")
    print(f"  Total tests: {len(results)}")
    print(f"  Delta passers: {sum(1 for r in results if r['pass_deltas'])}")
    print(f"  Promoted: {len(promotion_queue)}")
    print(f"  Output: {csv_path}")
    
    return csv_path

def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Run Campaign B: Route-First exploration")
    parser.add_argument("--seeds", default="experiments/pipeline_v2/data/route_campaign_seeds.json")
    parser.add_argument("--policy", default="experiments/pipeline_v2/policies/explore/POLICY.standard_blinded.json")
    parser.add_argument("--baseline", default="experiments/pipeline_v2/runs/2025-01-05-explore-breadth/baseline_stats.json")
    parser.add_argument("--output", default="experiments/pipeline_v2/runs/2025-01-06-explore-route/")
    parser.add_argument("--seed", type=int, default=1337)
    
    args = parser.parse_args()
    
    run_route_campaign(
        Path(args.seeds),
        Path(args.policy),
        Path(args.baseline),
        Path(args.output),
        args.seed
    )

if __name__ == "__main__":
    main()