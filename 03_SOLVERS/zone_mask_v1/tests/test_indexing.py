#!/usr/bin/env python3
"""
Test Indexing - Verify control indices are within zones, not in gaps
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_control_indices_in_zones():
    """Verify control indices are covered by zones"""
    print("Testing control indices coverage...")
    
    # Load control points
    control_path = Path(__file__).parent.parent.parent.parent / '02_DATA' / 'control_points.json'
    with open(control_path, 'r') as f:
        control_indices = json.load(f)
    
    print(f"Control indices: {control_indices}")
    
    # Standard zone configuration
    zones = {
        'head': (0, 20),
        'mid': (34, 73),  # Extended to cover control region
        'tail': (74, 96)
    }
    
    # Check each control index
    for idx in control_indices:
        in_zone = False
        for zone_name, (start, end) in zones.items():
            if start <= idx <= end:
                in_zone = True
                print(f"  Index {idx} is in {zone_name} zone")
                break
        
        if not in_zone:
            print(f"  ❌ ERROR: Index {idx} is in a GAP!")
            return False
    
    print("✓ All control indices are within zones")
    return True

def test_ct_positions():
    """Verify ciphertext at control positions"""
    print("\nTesting ciphertext at control positions...")
    
    # Load ciphertext
    ct_path = Path(__file__).parent.parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
    with open(ct_path, 'r') as f:
        ciphertext = f.read().strip().upper()
    
    # Check control region
    control_ct = ciphertext[63:74]
    expected = "NYPVTTMZFPK"
    
    print(f"CT[63:74] = '{control_ct}'")
    print(f"Expected  = '{expected}'")
    
    if control_ct == expected:
        print("✓ Ciphertext at control positions is correct")
        return True
    else:
        print("❌ Ciphertext mismatch at control positions!")
        return False

def test_zone_gaps():
    """Check for gaps between zones"""
    print("\nChecking for zone gaps...")
    
    zones = [
        ('head', 0, 20),
        ('mid', 34, 73),
        ('tail', 74, 96)
    ]
    
    # Check coverage
    covered = set()
    for name, start, end in zones:
        for i in range(start, end + 1):
            covered.add(i)
    
    # Find gaps
    gaps = []
    for i in range(97):
        if i not in covered:
            gaps.append(i)
    
    if gaps:
        print(f"Gaps found at positions: {gaps}")
        # Group consecutive gaps
        gap_ranges = []
        start = gaps[0]
        end = gaps[0]
        for i in range(1, len(gaps)):
            if gaps[i] == end + 1:
                end = gaps[i]
            else:
                gap_ranges.append((start, end))
                start = gaps[i]
                end = gaps[i]
        gap_ranges.append((start, end))
        
        for start, end in gap_ranges:
            print(f"  Gap: positions {start}-{end}")
    else:
        print("✓ No gaps in zone coverage")
    
    return len(gaps) > 0

def main():
    print("INDEXING VALIDATION TESTS")
    print("=" * 60)
    
    # Run tests
    test_control_indices_in_zones()
    test_ct_positions()
    test_zone_gaps()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("- Control indices must be 63-73 (zero-based)")
    print("- MID zone must extend to position 73")
    print("- No processing should occur in gaps")

if __name__ == '__main__':
    main()