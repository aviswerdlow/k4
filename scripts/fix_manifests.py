#!/usr/bin/env python3
"""
Fix all manifests to use correct zone boundaries and control indices
"""

import json
import os
from pathlib import Path

def fix_manifest(manifest_path):
    """Fix a single manifest with correct zones and indices"""
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Update zones to include control region in MID
    manifest['zones'] = {
        'head': {'start': 0, 'end': 20},
        'mid': {'start': 34, 'end': 73},  # Extended to cover control
        'tail': {'start': 74, 'end': 96}
    }
    
    # Update control indices to zero-based
    manifest['control']['indices'] = [63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73]
    
    # Save fixed manifest
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Fixed: {Path(manifest_path).name}")

def main():
    base_dir = Path(__file__).parent.parent / '04_EXPERIMENTS' / 'phase3_zone' / 'configs'
    
    print("Fixing manifests with correct zone boundaries...")
    print("=" * 60)
    
    # List of manifests to fix
    manifests = [
        'batch_a_A1.json', 'batch_a_A2.json', 'batch_a_A3.json',
        'batch_a_A4.json', 'batch_a_A5.json', 'batch_a_A6.json', 'batch_a_A7.json',
        'batch_b_B1.json', 'batch_b_B2.json', 'batch_b_B3.json',
        'batch_c_C1.json', 'batch_c_C2.json'
    ]
    
    for manifest_name in manifests:
        manifest_path = base_dir / manifest_name
        if manifest_path.exists():
            fix_manifest(manifest_path)
        else:
            print(f"Not found: {manifest_name}")
    
    print("\n" + "=" * 60)
    print("All manifests updated with:")
    print("- MID zone: 34-73 (includes control region)")
    print("- Control indices: 63-73 (zero-based)")

if __name__ == '__main__':
    main()