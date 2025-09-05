#!/usr/bin/env python3
"""
extract_heads.py - Extract candidate heads from permutation JSON files
"""

import json
import argparse
from pathlib import Path


def extract_head(perm_file, output_dir):
    """
    Extract head (positions 0-74) from permutation file.
    
    Args:
        perm_file: path to permutation JSON file
        output_dir: where to save the head text file
    """
    # Load permutation data
    with open(perm_file, 'r') as f:
        data = json.load(f)
    
    # Get the permuted text
    if 'permuted_text' in data:
        full_text = data['permuted_text']
    elif 'text' in data:
        full_text = data['text']
    else:
        raise ValueError(f"Could not find permuted text in {perm_file}")
    
    # Extract head (first 75 characters)
    head = full_text[:75]
    
    # Create output filename based on input
    perm_path = Path(perm_file)
    label = perm_path.stem  # e.g., "GRID_W14_ROWS"
    
    output_path = Path(output_dir) / f"{label}_head.txt"
    
    # Write head to file
    with open(output_path, 'w') as f:
        f.write(head)
    
    print(f"Extracted {label}: {head}")
    return label, head


def main():
    parser = argparse.ArgumentParser(description='Extract heads from permutation files')
    parser.add_argument('--perm-dir', default='experiments/cadence_panel/data/permutations',
                       help='Directory with permutation JSON files')
    parser.add_argument('--out-dir', default='experiments/cadence_panel/data/heads',
                       help='Output directory for head files')
    parser.add_argument('--files', nargs='+', 
                       default=['GRID_W14_ROWS.json', 'GRID_W10_NW.json'],
                       help='Specific permutation files to process')
    
    args = parser.parse_args()
    
    # Create output directory
    out_path = Path(args.out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    # Process each file
    perm_dir = Path(args.perm_dir)
    
    for filename in args.files:
        perm_file = perm_dir / filename
        if perm_file.exists():
            try:
                label, head = extract_head(perm_file, out_path)
                print(f"✓ {label}: {len(head)} chars")
            except Exception as e:
                print(f"✗ Error processing {filename}: {e}")
        else:
            print(f"✗ File not found: {perm_file}")
    
    print(f"\nHeads saved to: {out_path}")


if __name__ == '__main__':
    main()