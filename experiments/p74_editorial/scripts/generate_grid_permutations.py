#!/usr/bin/env python3
"""
Generate GRID permutation files for P74 editorial study.
Creates GRID_W14_ROWS and GRID_W10_NW permutations.
"""

import json
from pathlib import Path

def generate_grid_w14_rows():
    """Generate GRID_W14_ROWS permutation (14-wide row-major)"""
    permutation = []
    width = 14
    height = 7
    
    # Row-major order
    for row in range(height):
        for col in range(width):
            idx = row * width + col
            if idx < 97:  # Only up to index 96
                permutation.append(idx)
    
    return {
        "name": "GRID_W14_ROWS",
        "description": "14-wide grid, row-major order",
        "width": width,
        "height": height,
        "permutation": permutation
    }

def generate_grid_w10_nw():
    """Generate GRID_W10_NW permutation (10-wide, NW diagonal)"""
    permutation = []
    width = 10
    height = 10
    
    # NW diagonal pattern
    # Start from top-left, go diagonally
    visited = set()
    
    # Diagonals starting from first row
    for start_col in range(width):
        row, col = 0, start_col
        while row < height and col >= 0:
            idx = row * width + col
            if idx < 97 and idx not in visited:
                permutation.append(idx)
                visited.add(idx)
            row += 1
            col -= 1
    
    # Diagonals starting from first column (skip 0,0 already done)
    for start_row in range(1, height):
        row, col = start_row, width - 1
        while row < height and col >= 0:
            idx = row * width + col
            if idx < 97 and idx not in visited:
                permutation.append(idx)
                visited.add(idx)
            row += 1
            col -= 1
    
    # Fill any missing indices in order
    for i in range(97):
        if i not in visited:
            permutation.append(i)
    
    return {
        "name": "GRID_W10_NW",
        "description": "10-wide grid, NW diagonal order",
        "width": width,
        "height": height,
        "permutation": permutation[:97]  # Ensure exactly 97 elements
    }

def main():
    """Generate and save permutation files"""
    
    # Create output directory
    out_dir = Path("experiments/p74_editorial/data/permutations")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate GRID_W14_ROWS
    grid_w14 = generate_grid_w14_rows()
    with open(out_dir / "GRID_W14_ROWS.json", "w") as f:
        json.dump(grid_w14, f, indent=2)
    print(f"Generated GRID_W14_ROWS with {len(grid_w14['permutation'])} elements")
    
    # Generate GRID_W10_NW
    grid_w10 = generate_grid_w10_nw()
    with open(out_dir / "GRID_W10_NW.json", "w") as f:
        json.dump(grid_w10, f, indent=2)
    print(f"Generated GRID_W10_NW with {len(grid_w10['permutation'])} elements")
    
    print(f"\nPermutation files saved to: {out_dir}")
    
    return 0


if __name__ == "__main__":
    exit(main())