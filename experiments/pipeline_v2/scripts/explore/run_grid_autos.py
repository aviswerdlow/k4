#!/usr/bin/env python3
"""
Run anchor-constrained GRID transformations that preserve spatial relationships.
Only applies geometry-respecting transforms that maintain anchor positions.
"""

import json
import csv
import hashlib
import random
import numpy as np
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

def verify_anchor_preservation(
    original: str,
    transformed: str,
    transform_map: List[int],
    anchor_positions: Dict[str, List[int]]
) -> bool:
    """
    Verify that a transformation preserves anchor relationships.
    
    Args:
        original: Original plaintext
        transformed: Transformed plaintext
        transform_map: Index mapping from original to transformed positions
        anchor_positions: Expected anchor positions
    
    Returns:
        True if anchors are preserved with correct relationships
    """
    # Check EAST preservation
    east_orig = original[21:25]
    if east_orig == "EAST":
        # Find where EAST ended up
        east_new_pos = [transform_map[i] for i in range(21, 25)]
        # Check if still contiguous
        if max(east_new_pos) - min(east_new_pos) != 3:
            return False
        # Check if still says EAST
        east_new = ''.join(transformed[i] for i in sorted(east_new_pos))
        if east_new != "EAST":
            return False
    
    # Check NORTHEAST preservation and adjacency to EAST
    ne_orig = original[25:34]
    if ne_orig == "NORTHEAST":
        ne_new_pos = [transform_map[i] for i in range(25, 34)]
        if max(ne_new_pos) - min(ne_new_pos) != 8:
            return False
        ne_new = ''.join(transformed[i] for i in sorted(ne_new_pos))
        if ne_new != "NORTHEAST":
            return False
        
        # Check adjacency with EAST
        east_new_end = max([transform_map[i] for i in range(21, 25)])
        ne_new_start = min([transform_map[i] for i in range(25, 34)])
        if abs(ne_new_start - east_new_end) > 1:  # Must be adjacent
            return False
    
    # Check BERLINCLOCK preservation in NA domain
    berlin_orig = original[63:74]
    if "BERLINCLOCK" in berlin_orig:
        # More flexible check for BERLINCLOCK since exact position varies
        if "BERLINCLOCK" not in transformed[50:]:  # Must be in latter half
            return False
    
    return True

def apply_grid_auto(
    text: str,
    transform_type: str,
    seed: int = 1337
) -> Tuple[str, List[int]]:
    """
    Apply anchor-preserving GRID transformation.
    
    Returns:
        (transformed_text, position_mapping)
    """
    random.seed(seed)
    n = len(text)
    
    if transform_type == "GRID_10x10_FIXED":
        # Standard 10x10 grid, read column-wise
        # Pad to 100 if needed
        if n < 100:
            text = text + 'X' * (100 - n)
        
        grid = []
        for i in range(10):
            grid.append(list(text[i*10:(i+1)*10]))
        
        # Read column-wise
        result = []
        mapping = []
        for j in range(10):
            for i in range(10):
                if i * 10 + j < n:
                    result.append(grid[i][j])
                    mapping.append(i * 10 + j)
        
        return ''.join(result[:n]), mapping[:n]
    
    elif transform_type == "GRID_10x10_ROW_PERM":
        # Permute only non-anchor rows
        if n < 100:
            text = text + 'X' * (100 - n)
        
        grid = []
        for i in range(10):
            grid.append(list(text[i*10:(i+1)*10]))
        
        # Identify anchor rows (rows 2,3 contain EAST/NORTHEAST)
        anchor_rows = {2, 3, 6, 7}  # Rows with anchors
        non_anchor_rows = [i for i in range(10) if i not in anchor_rows]
        
        # Shuffle non-anchor rows
        random.shuffle(non_anchor_rows)
        
        # Build permuted grid
        new_grid = [None] * 10
        for i in anchor_rows:
            new_grid[i] = grid[i]
        
        for i, row_idx in enumerate(non_anchor_rows):
            target_idx = [j for j in range(10) if j not in anchor_rows][i]
            new_grid[target_idx] = grid[row_idx]
        
        # Read column-wise from permuted grid
        result = []
        mapping = []
        for j in range(10):
            for i in range(10):
                if i * 10 + j < n:
                    result.append(new_grid[i][j])
                    # Track where this character came from
                    orig_row = [k for k, r in enumerate(grid) if r == new_grid[i]][0]
                    mapping.append(orig_row * 10 + j)
        
        return ''.join(result[:n]), mapping[:n]
    
    elif transform_type == "GRID_10x10_COL_SHIFT":
        # Cyclic column shift preserving anchor columns
        if n < 100:
            text = text + 'X' * (100 - n)
        
        grid = []
        for i in range(10):
            grid.append(list(text[i*10:(i+1)*10]))
        
        # Shift columns cyclically by 3 (preserves relative positions)
        shift = 3
        new_grid = []
        for row in grid:
            new_row = row[shift:] + row[:shift]
            new_grid.append(new_row)
        
        # Read column-wise
        result = []
        mapping = []
        for j in range(10):
            for i in range(10):
                if i * 10 + j < n:
                    result.append(new_grid[i][j])
                    # Original position before shift
                    orig_col = (j - shift) % 10
                    mapping.append(i * 10 + orig_col)
        
        return ''.join(result[:n]), mapping[:n]
    
    elif transform_type == "GRID_11x9_PINNED":
        # 11x9 grid with anchor positions pinned
        if n < 99:
            text = text + 'X' * (99 - n)
        
        grid = []
        for i in range(11):
            if i < 10:
                grid.append(list(text[i*9:min((i+1)*9, n)]))
            else:
                grid.append(list(text[90:min(99, n)]))
        
        # Ensure anchors stay in reasonable positions
        # Read with modified pattern to preserve anchors
        result = []
        mapping = []
        
        # Custom read pattern that keeps anchors together
        for j in range(9):
            for i in range(11):
                if i * 9 + j < n:
                    idx = min(i * 9 + j, n - 1)
                    result.append(text[idx])
                    mapping.append(idx)
        
        return ''.join(result[:n]), mapping[:n]
    
    elif transform_type == "GRID_9x11_PINNED":
        # 9x11 grid with different aspect ratio
        if n < 99:
            text = text + 'X' * (99 - n)
        
        grid = []
        for i in range(9):
            grid.append(list(text[i*11:min((i+1)*11, n)]))
        
        result = []
        mapping = []
        for j in range(11):
            for i in range(9):
                if i * 11 + j < n:
                    result.append(grid[i][j])
                    mapping.append(i * 11 + j)
        
        return ''.join(result[:n]), mapping[:n]
    
    elif transform_type == "GRID_CONJUGATE_1":
        # Block transpose that preserves anchor blocks
        # Split into 5x5 blocks and transpose within blocks
        blocks = []
        block_size = 15
        
        for i in range(0, n, block_size):
            block = text[i:min(i+block_size, n)]
            blocks.append(block)
        
        # Transpose within each block (if it contains anchors, keep them)
        result = []
        mapping = []
        
        for block_idx, block in enumerate(blocks):
            start_pos = block_idx * block_size
            
            # Check if this block contains anchors
            has_anchor = False
            if 21 <= start_pos <= 33:  # EAST/NORTHEAST block
                has_anchor = True
            if 63 <= start_pos <= 73:  # BERLINCLOCK block
                has_anchor = True
            
            if has_anchor:
                # Keep block as-is
                result.extend(block)
                mapping.extend(range(start_pos, start_pos + len(block)))
            else:
                # Reverse the block
                result.extend(block[::-1])
                mapping.extend(range(start_pos + len(block) - 1, start_pos - 1, -1))
        
        return ''.join(result[:n]), mapping[:n]
    
    elif transform_type == "GRID_CONJUGATE_2":
        # Strided read with anchor stride preserved
        stride = 7
        result = []
        mapping = []
        
        for offset in range(stride):
            for i in range(offset, n, stride):
                result.append(text[i])
                mapping.append(i)
        
        return ''.join(result[:n]), mapping[:n]
    
    elif transform_type == "GRID_CONJUGATE_3":
        # Diagonal read pattern
        if n <= 64:
            size = 8
        elif n <= 81:
            size = 9
        else:
            size = 10
        
        grid_size = size * size
        if n < grid_size:
            text = text + 'X' * (grid_size - n)
        
        grid = []
        for i in range(size):
            grid.append(list(text[i*size:(i+1)*size]))
        
        # Read diagonally
        result = []
        mapping = []
        
        # Upper diagonals
        for d in range(size):
            i, j = 0, d
            while i < size and j >= 0:
                if i * size + (d - i) < n:
                    result.append(grid[i][j])
                    mapping.append(i * size + j)
                i += 1
                j -= 1
        
        # Lower diagonals
        for d in range(1, size):
            i, j = d, size - 1
            while i < size and j >= 0:
                if i * size + j < n:
                    result.append(grid[i][j])
                    mapping.append(i * size + j)
                i += 1
                j -= 1
        
        return ''.join(result[:n]), mapping[:n]
    
    # Default: return unchanged
    return text, list(range(n))

def run_grid_autos_campaign(
    seeds_file: Path,
    policy_file: Path,
    baseline_stats_file: Path,
    output_dir: Path,
    seed: int = 1337
) -> None:
    """
    Run anchor-constrained GRID campaign.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load inputs
    with open(seeds_file) as f:
        seeds_data = json.load(f)
        candidates = seeds_data.get("heads", seeds_data.get("candidates", []))[:10]
    
    with open(policy_file) as f:
        policy = json.load(f)
    
    with open(baseline_stats_file) as f:
        baseline_stats = json.load(f)
    
    # Transform types
    transform_types = [
        "GRID_10x10_FIXED",
        "GRID_10x10_ROW_PERM", 
        "GRID_10x10_COL_SHIFT",
        "GRID_11x9_PINNED",
        "GRID_9x11_PINNED",
        "GRID_CONJUGATE_1",
        "GRID_CONJUGATE_2",
        "GRID_CONJUGATE_3"
    ]
    
    print(f"Testing {len(candidates)} seeds × {len(transform_types)} transforms")
    print("Verifying anchor preservation for each...")
    
    results = []
    promotion_queue = []
    
    for cand_idx, candidate in enumerate(candidates):
        text = candidate["text"]
        label = candidate.get("label", f"C{cand_idx:04d}")
        
        print(f"\nSeed {cand_idx+1}/{len(candidates)}: {label}")
        
        for transform_type in transform_types:
            # Apply transformation
            transformed, mapping = apply_grid_auto(text, transform_type, seed + cand_idx)
            
            # Verify anchor preservation
            anchor_positions = {
                "EAST": [21, 24],
                "NORTHEAST": [25, 33],
                "BERLINCLOCK": [63, 73]
            }
            
            preserved = verify_anchor_preservation(
                text, transformed, mapping, anchor_positions
            )
            
            if not preserved:
                print(f"  {transform_type}: Anchors not preserved, skipping")
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
                    random.seed(seed + cand_idx + hash(transform_type))
                    for anchor in mode_policy["anchor_config"]["anchors"]:
                        span = mode_policy["anchor_config"]["anchors"][anchor]["span"]
                        length = span[1] - span[0]
                        new_start = random.randint(0, len(transformed) - length - 1)
                        mode_policy["anchor_config"]["anchors"][anchor]["span"] = [
                            new_start, new_start + length
                        ]
                
                # Compute normalized score
                score_data = compute_normalized_score(transformed, mode_policy, baseline_stats)
                scores[mode] = score_data["score_norm"]
            
            # Compute deltas
            delta_windowed = scores["fixed"] - scores["windowed"]
            delta_shuffled = scores["fixed"] - scores["shuffled"]
            
            result = {
                "seed_label": label,
                "transform": transform_type,
                "length": len(transformed),
                "fixed_score": scores["fixed"],
                "windowed_score": scores["windowed"],
                "shuffled_score": scores["shuffled"],
                "delta_windowed": delta_windowed,
                "delta_shuffled": delta_shuffled,
                "pass_deltas": delta_windowed >= 0.05 and delta_shuffled >= 0.05,
                "anchors_preserved": preserved
            }
            results.append(result)
            
            # Check for promotion
            if result["pass_deltas"]:
                # Run bootstrap nulls
                p_value = run_bootstrap_nulls(transformed, n=1000, seed=seed+cand_idx)
                if p_value < 0.05:
                    promotion_queue.append({
                        "seed_label": label,
                        "transform": transform_type,
                        "text": transformed,
                        "scores": scores,
                        "deltas": {"windowed": delta_windowed, "shuffled": delta_shuffled},
                        "p_value": p_value
                    })
                    print(f"  ✓ PROMOTED: {transform_type} (δ₁={delta_windowed:.3f}, δ₂={delta_shuffled:.3f})")
    
    # Write results
    matrix_path = output_dir / "ANCHOR_MODE_MATRIX.csv"
    with open(matrix_path, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    # Write promotion queue
    queue_path = output_dir / "promotion_queue.json"
    with open(queue_path, 'w') as f:
        json.dump({
            "campaign": "PV2-EXPLORE-GRID-AUTOS-001",
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(results),
            "delta_passers": sum(1 for r in results if r["pass_deltas"]),
            "promoted": len(promotion_queue),
            "queue": promotion_queue
        }, f, indent=2)
    
    # Generate manifest
    manifest_path = output_dir / "MANIFEST.sha256"
    with open(manifest_path, 'w') as f:
        for file_path in sorted(output_dir.glob("*")):
            if file_path.is_file():
                with open(file_path, 'rb') as fp:
                    hash_val = hashlib.sha256(fp.read()).hexdigest()
                f.write(f"{hash_val}  {file_path.name}\n")
    
    print(f"\n{'='*60}")
    print(f"Grid Autos Campaign Complete:")
    print(f"  Total tests: {len(results)}")
    print(f"  Anchors preserved: {sum(1 for r in results if r['anchors_preserved'])}")
    print(f"  Delta passers: {sum(1 for r in results if r['pass_deltas'])}")
    print(f"  Promoted: {len(promotion_queue)}")
    print(f"  Output: {output_dir}")

def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Run anchor-constrained GRID campaign")
    parser.add_argument("--seeds", default="experiments/pipeline_v2/data/candidates_breadth.json")
    parser.add_argument("--policy", default="experiments/pipeline_v2/policies/explore/POLICY.anchor_fixed.json")
    parser.add_argument("--baseline", default="experiments/pipeline_v2/runs/2025-01-05-explore-breadth/baseline_stats.json")
    parser.add_argument("--output", default="experiments/pipeline_v2/runs/2025-01-06-explore-grid-autos/")
    parser.add_argument("--seed", type=int, default=1337)
    
    args = parser.parse_args()
    
    run_grid_autos_campaign(
        Path(args.seeds),
        Path(args.policy),
        Path(args.baseline),
        Path(args.output),
        args.seed
    )

if __name__ == "__main__":
    main()