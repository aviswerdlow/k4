#!/usr/bin/env python3
"""
Fix for Skeleton Survey v3 - Proper wheel solving and derivation
"""

import sys
import json
from pathlib import Path

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))
from core_hardening_utils import *


def derive_pt_from_wheels(ct: str, class_func, wheels_by_class: dict) -> str:
    """
    Derive plaintext from wheels using slot arithmetic.
    
    Each wheel has: family, L (period), phase, residues
    """
    pt = []
    for i, ch in enumerate(ct):
        cls = class_func(i)
        wheel = wheels_by_class.get(cls)
        if wheel is None:
            pt.append('?')
            continue
        
        C = ord(ch) - ord('A')
        L = wheel.get('L', wheel.get('period', 1))
        phase = wheel.get('phase', 0)
        residues = wheel.get('residues', wheel.get('key', []))
        
        if not residues:
            pt.append('?')
            continue
            
        slot = (i - phase) % L
        if slot >= len(residues):
            pt.append('?')
            continue
            
        K = residues[slot]
        fam = wheel['family']
        
        if fam == 'vigenere':
            P = (C - K) % 26
        elif fam == 'beaufort':
            P = (K - C) % 26
        elif fam == 'variant_beaufort':
            P = (C + K) % 26
        else:
            pt.append('?')
            continue
            
        pt.append(chr(P + ord('A')))
    
    return ''.join(pt)


def solve_wheels_for_pattern(ct: str, pt: str, class_func, enforce_option_a=True) -> dict:
    """
    Solve wheels for a pattern using full plaintext.
    
    Returns dict of {class_id: wheel_config} or None if infeasible.
    """
    # Group indices by class
    class_indices = {}
    for i in range(len(ct)):
        cid = class_func(i)
        class_indices.setdefault(cid, []).append(i)
    
    # Get anchor positions for Option-A
    anchor_positions = set()
    if enforce_option_a:
        # Standard four anchors
        anchor_positions.update(range(0, 10))   # PALIMPSEST
        anchor_positions.update(range(26, 34))  # ABSCISSA
        anchor_positions.update(range(54, 59))  # LAYER
        anchor_positions.update(range(64, 69))  # IDBYROWS
    
    wheels = {}
    
    for cid, indices in class_indices.items():
        # Try different wheel families and periods
        best_wheel = None
        
        for family in ['vigenere', 'beaufort', 'variant_beaufort']:
            for L in range(1, 26):  # Try periods 1-25
                for phase in range(L):  # Try phases 0..(L-1)
                    # Derive residues from ct/pt pairs
                    residues = {}
                    valid = True
                    
                    for idx in indices:
                        C = ord(ct[idx]) - ord('A')
                        P = ord(pt[idx]) - ord('A')
                        slot = (idx - phase) % L
                        
                        # Calculate required K for this position
                        if family == 'vigenere':
                            K = (C - P) % 26
                        elif family == 'beaufort':
                            K = (P + C) % 26
                        elif family == 'variant_beaufort':
                            K = (P - C) % 26
                        
                        # Check consistency
                        if slot in residues:
                            if residues[slot] != K:
                                valid = False
                                break
                        else:
                            residues[slot] = K
                        
                        # Check Option-A at anchors
                        if enforce_option_a and idx in anchor_positions:
                            if family in ['vigenere', 'beaufort'] and K == 0:
                                valid = False
                                break
                    
                    if valid and len(residues) == L:
                        # Found a valid wheel
                        best_wheel = {
                            'family': family,
                            'L': L,
                            'period': L,
                            'phase': phase,
                            'residues': [residues[s] for s in range(L)],
                            'key': [residues[s] for s in range(L)]  # Compatibility
                        }
                        break
                
                if best_wheel:
                    break
            
            if best_wheel:
                break
        
        if best_wheel is None:
            return None
        
        wheels[cid] = best_wheel
    
    return wheels


def test_baseline():
    """Test that baseline pattern works correctly."""
    print("Testing baseline pattern...")
    
    # Load data
    with open('02_DATA/ciphertext_97.txt', 'r') as f:
        ct = f.read().strip()
    
    with open('02_DATA/plaintext_97.txt', 'r') as f:
        pt = f.read().strip()
    
    # Solve wheels for baseline
    wheels = solve_wheels_for_pattern(ct, pt, compute_baseline_class, enforce_option_a=True)
    
    if wheels is None:
        print("ERROR: Baseline solve failed!")
        return False
    
    print(f"Solved {len(wheels)} wheels for baseline:")
    for cid, wheel in sorted(wheels.items()):
        print(f"  Class {cid}: {wheel['family']}, L={wheel['L']}, phase={wheel['phase']}, "
              f"residues[:5]={wheel['residues'][:5]}")
    
    # Derive plaintext
    derived = derive_pt_from_wheels(ct, compute_baseline_class, wheels)
    
    # Check SHA
    derived_sha = compute_sha256(derived)
    expected_sha = "4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79"
    
    if derived_sha == expected_sha:
        print(f"✓ Baseline test PASSED! SHA matches: {derived_sha[:16]}...")
        return True
    else:
        print(f"✗ Baseline test FAILED!")
        print(f"  Expected SHA: {expected_sha[:16]}...")
        print(f"  Got SHA: {derived_sha[:16]}...")
        
        # Show first mismatches
        mismatches = []
        for i in range(len(pt)):
            if i < len(derived) and pt[i] != derived[i]:
                cls = compute_baseline_class(i)
                mismatches.append((i, cls, pt[i], derived[i]))
        
        print(f"  First 10 mismatches:")
        for i, cls, expected, got in mismatches[:10]:
            print(f"    i={i}, class={cls}: expected={expected}, got={got}")
        
        return False


if __name__ == "__main__":
    success = test_baseline()
    sys.exit(0 if success else 1)