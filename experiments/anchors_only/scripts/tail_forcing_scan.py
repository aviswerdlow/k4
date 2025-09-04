#!/usr/bin/env python3
"""
Anchors-Only Tail Forcing Scan

Pure algebraic coverage test: do anchors alone fix all key residues 
needed to determine tail letters 75..96 for pencil-and-paper cipher models?

No language scoring, no phrase gates - just residue coverage analysis.
"""

import json
import csv
import argparse
from pathlib import Path
from datetime import datetime
import os

def load_ciphertext(ct_path):
    """Load ciphertext as A..Z string"""
    with open(ct_path, 'r') as f:
        ct = f.read().strip()
    # Convert to 0-25 integer array
    return [ord(c) - ord('A') for c in ct]

def load_permutation(perm_path):
    """Load permutation JSON - assumes NA-only (anchors fixed by exclusion)"""
    with open(perm_path, 'r') as f:
        perm_data = json.load(f)
    
    route_id = perm_data['id']
    na_indices = perm_data['NA']
    order = perm_data['order_abs_dst']
    
    # For NA-only permutations, anchors should NOT be in the NA list
    anchor_ranges = [(21, 24), (25, 33), (63, 73)]  # EAST, NORTHEAST, BERLINCLOCK
    anchor_indices = []
    for start, end in anchor_ranges:
        anchor_indices.extend(range(start, end + 1))
    
    # Verify no anchors are in the permutation domain (NA-only constraint)
    anchor_in_na = [a for a in anchor_indices if a in na_indices]
    if anchor_in_na:
        raise ValueError(f"Route {route_id} includes anchors {anchor_in_na} in permutation domain - violates NA-only constraint")
    
    return route_id, na_indices, order

def compute_residue(index, classing, L, phase):
    """Compute key residue for given index under classing/period/phase"""
    if classing == 'single_key':
        return (index + phase) % L
    elif classing == 'c6a':
        # c6a: 6 classes, 3 period pairs
        cid = ((index % 2) * 3) + (index % 3)
        # For simplicity, assume uniform period L for all classes
        # and phase applied uniformly (this is a simplified c6a model)
        return (index + phase) % L  # Simplified - real c6a is more complex
    else:
        raise ValueError(f"Unknown classing: {classing}")

def solve_key_value(ct_val, pt_val, family):
    """Solve for key value given C, P, and cipher family"""
    if family == 'vigenere':
        # P = (C - K) mod 26, so K = (C - P) mod 26
        return (ct_val - pt_val) % 26
    elif family == 'variant_beaufort':
        # P = (K - C) mod 26, so K = (P + C) mod 26
        return (pt_val + ct_val) % 26
    elif family == 'beaufort':
        # P = (K + C) mod 26, so K = (P - C) mod 26
        return (pt_val - ct_val) % 26
    else:
        raise ValueError(f"Unknown family: {family}")

def decrypt_letter(ct_val, key_val, family):
    """Decrypt single letter given C, K, and family"""
    if family == 'vigenere':
        return (ct_val - key_val) % 26
    elif family == 'variant_beaufort':
        return (key_val - ct_val) % 26
    elif family == 'beaufort':
        return (key_val + ct_val) % 26
    else:
        raise ValueError(f"Unknown family: {family}")

def test_anchor_forcing(ct, na_indices, order, route_id, family, classing, L, phase):
    """Test whether anchors force all tail residues for this model"""
    
    # Anchor positions and expected plaintext values
    anchors = {
        21: ord('E') - ord('A'), 22: ord('A') - ord('A'), 23: ord('S') - ord('A'), 24: ord('T') - ord('A'),  # EAST
        25: ord('N') - ord('A'), 26: ord('O') - ord('A'), 27: ord('R') - ord('A'), 28: ord('T') - ord('A'),  # NORT
        29: ord('H') - ord('A'), 30: ord('E') - ord('A'), 31: ord('A') - ord('A'), 32: ord('S') - ord('A'), 33: ord('T') - ord('A'),  # HEAST
        63: ord('B') - ord('A'), 64: ord('E') - ord('A'), 65: ord('R') - ord('A'), 66: ord('L') - ord('A'),  # BERL
        67: ord('I') - ord('A'), 68: ord('N') - ord('A'), 69: ord('C') - ord('A'), 70: ord('L') - ord('A'),  # INCL
        71: ord('O') - ord('A'), 72: ord('C') - ord('A'), 73: ord('K') - ord('A')   # OCK
    }
    
    forced_residues = {}
    anchor_collisions = 0
    illegal_passthrough = False
    
    # Process each anchor position
    for anchor_idx, expected_pt in anchors.items():
        # For NA-only permutations, anchors are NOT in the permutation domain
        # They remain at their original positions unchanged
        
        # Compute residue for this anchor at its original position
        residue = compute_residue(anchor_idx, classing, L, phase)
        
        # Solve for key value at this residue
        ct_val = ct[anchor_idx]
        key_val = solve_key_value(ct_val, expected_pt, family)
        
        # Check for illegal pass-through (K=0 for Vig/VB)
        if key_val == 0 and family in ['vigenere', 'variant_beaufort']:
            illegal_passthrough = True
        
        # Check for collision
        if residue in forced_residues:
            if forced_residues[residue] != key_val:
                anchor_collisions += 1
        else:
            forced_residues[residue] = key_val
    
    if anchor_collisions > 0 or illegal_passthrough:
        return {
            'feasible': False,
            'forced_residues': len(forced_residues),
            'anchor_collisions': anchor_collisions,
            'illegal_passthrough': illegal_passthrough,
            'tail_forced': False,
            'implied_tail': ''
        }
    
    # Check tail coverage (positions 75-96)
    tail_indices = list(range(75, 97))
    tail_residues_needed = set()
    tail_forced = True
    implied_tail = []
    
    for tail_idx in tail_indices:
        # For NA-only permutations, check if this tail position is moved
        if tail_idx in na_indices:
            # Find where this tail position maps after permutation
            na_pos = na_indices.index(tail_idx)
            dst_idx = order[na_pos]
        else:
            # Position not in permutation domain, stays at original position
            dst_idx = tail_idx
        
        # Compute residue needed for decryption at destination position
        residue = compute_residue(dst_idx, classing, L, phase)
        tail_residues_needed.add(residue)
        
        if residue not in forced_residues:
            tail_forced = False
            implied_tail.append('_')  # Unforced position
        else:
            # Decrypt this tail position
            ct_val = ct[tail_idx]
            key_val = forced_residues[residue]
            pt_val = decrypt_letter(ct_val, key_val, family)
            implied_tail.append(chr(pt_val + ord('A')))
    
    return {
        'feasible': True,
        'forced_residues': len(forced_residues),
        'anchor_collisions': anchor_collisions,
        'illegal_passthrough': illegal_passthrough,
        'tail_forced': tail_forced,
        'implied_tail': ''.join(implied_tail)
    }

def main():
    parser = argparse.ArgumentParser(description='Anchors-only tail forcing scan')
    parser.add_argument('--ct', required=True, help='Path to ciphertext file')
    parser.add_argument('--perms_dir', required=True, help='Directory with permutation JSON files')
    parser.add_argument('--policy', required=True, help='Path to policy JSON')
    parser.add_argument('--out', required=True, help='Output directory')
    parser.add_argument('--classing', default='single_key', help='Key classing (single_key|c6a)')
    parser.add_argument('--families', default='vigenere,beaufort,variant_beaufort', help='Cipher families')
    parser.add_argument('--L_min', type=int, default=2, help='Minimum period')
    parser.add_argument('--L_max', type=int, default=22, help='Maximum period')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.out, exist_ok=True)
    
    # Load ciphertext
    ct = load_ciphertext(args.ct)
    
    # Load permutations
    perm_files = list(Path(args.perms_dir).glob('*.json'))
    permutations = []
    
    for perm_file in perm_files:
        try:
            route_id, na_indices, order = load_permutation(perm_file)
            permutations.append((route_id, na_indices, order, str(perm_file)))
            print(f"✅ Loaded {route_id} (anchors fixed)")
        except ValueError as e:
            print(f"❌ Skipped {perm_file}: {e}")
    
    # Parse families
    families = args.families.split(',')
    
    # Results collection
    results = []
    
    print(f"\n🔬 Running anchors-only forcing scan...")
    print(f"   Classing: {args.classing}")
    print(f"   Families: {families}")
    print(f"   Periods: L={args.L_min}..{args.L_max}")
    print(f"   Routes: {len(permutations)}")
    
    total_tests = len(permutations) * len(families) * (args.L_max - args.L_min + 1)
    test_count = 0
    
    # Test each combination
    for route_id, na_indices, order, perm_file in permutations:
        for family in families:
            for L in range(args.L_min, args.L_max + 1):
                # Test all phases for this period
                for phase in range(L):
                    test_count += 1
                    if test_count % 1000 == 0:
                        print(f"   Progress: {test_count}/{total_tests}")
                    
                    result = test_anchor_forcing(ct, na_indices, order, route_id, family, args.classing, L, phase)
                    
                    if result is None:
                        continue  # Skip invalid permutations
                    
                    # Record result
                    row = {
                        'route_id': route_id,
                        'family': family,
                        'classing': args.classing,
                        'L': L,
                        'phase': phase,
                        'feasible': result['feasible'],
                        'forced_residues': result['forced_residues'],
                        'tail_forced': result['tail_forced'],
                        'implied_tail': result['implied_tail'],
                        'anchor_collisions': result['anchor_collisions'],
                        'illegal_passthrough': result['illegal_passthrough']
                    }
                    results.append(row)
    
    print(f"✅ Completed {test_count} tests")
    
    # Write CSV summary
    csv_file = Path(args.out) / 'summary.csv'
    with open(csv_file, 'w', newline='') as f:
        fieldnames = ['route_id', 'family', 'classing', 'L', 'phase', 'feasible', 
                      'forced_residues', 'tail_forced', 'implied_tail', 
                      'anchor_collisions', 'illegal_passthrough']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"📄 Results written to {csv_file}")
    
    # Generate summary statistics
    feasible_results = [r for r in results if r['feasible']]
    tail_forced_results = [r for r in feasible_results if r['tail_forced']]
    
    print(f"\n📊 Summary:")
    print(f"   Total tests: {len(results)}")
    print(f"   Feasible models: {len(feasible_results)}")
    print(f"   Tail forced: {len(tail_forced_results)}")
    
    if tail_forced_results:
        # Check tail consistency
        unique_tails = set(r['implied_tail'] for r in tail_forced_results if r['implied_tail'])
        print(f"   Unique tail strings: {len(unique_tails)}")
        for tail in unique_tails:
            count = sum(1 for r in tail_forced_results if r['implied_tail'] == tail)
            print(f"     '{tail}': {count} models")
    
    return csv_file

if __name__ == '__main__':
    main()