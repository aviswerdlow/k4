#!/usr/bin/env python3
"""
Anchors + Multi-Class Tail Forcing Scan

Test whether adding multi-class repeating keys (c6a/c6b) removes anchor collisions
and algebraically forces the tail without seam or language constraints.

Pure algebraic coverage test with multi-class schedules.
"""

import json
import csv
import argparse
from pathlib import Path
from datetime import datetime
import os
import itertools

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

def compute_class_id(index, schedule):
    """Compute class ID for given index under c6a or c6b schedule"""
    if schedule == 'c6a':
        # c6a: ((i % 2) * 3) + (i % 3)
        return ((index % 2) * 3) + (index % 3)
    elif schedule == 'c6b':
        # c6b: ((i % 3) * 2) + (i % 2)
        return ((index % 3) * 2) + (index % 2)
    else:
        raise ValueError(f"Unknown schedule: {schedule}")

def compute_ordinal_in_class(index, schedule):
    """Compute ordinal position within class for given index"""
    if schedule == 'c6a':
        # For c6a, ordinal is floor(i / 6)
        return index // 6
    elif schedule == 'c6b':
        # For c6b, ordinal is floor(i / 6)  
        return index // 6
    else:
        raise ValueError(f"Unknown schedule: {schedule}")

def compute_residue_address(index, schedule, L_vec, phase_vec):
    """Compute residue address for given index under multi-class schedule"""
    class_id = compute_class_id(index, schedule)
    ordinal = compute_ordinal_in_class(index, schedule)
    
    L_k = L_vec[class_id]
    phase_k = phase_vec[class_id]
    
    residue = (ordinal + phase_k) % L_k
    return class_id, residue

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

def test_multiclass_forcing(ct, na_indices, order, route_id, family, schedule, L_vec, phase_vec):
    """Test whether anchors + multi-class schedule force all tail residues"""
    
    # Anchor positions and expected plaintext values
    anchors = {
        21: ord('E') - ord('A'), 22: ord('A') - ord('A'), 23: ord('S') - ord('A'), 24: ord('T') - ord('A'),  # EAST
        25: ord('N') - ord('A'), 26: ord('O') - ord('A'), 27: ord('R') - ord('A'), 28: ord('T') - ord('A'),  # NORT
        29: ord('H') - ord('A'), 30: ord('E') - ord('A'), 31: ord('A') - ord('A'), 32: ord('S') - ord('A'), 33: ord('T') - ord('A'),  # HEAST
        63: ord('B') - ord('A'), 64: ord('E') - ord('A'), 65: ord('R') - ord('A'), 66: ord('L') - ord('A'),  # BERL
        67: ord('I') - ord('A'), 68: ord('N') - ord('A'), 69: ord('C') - ord('A'), 70: ord('L') - ord('A'),  # INCL
        71: ord('O') - ord('A'), 72: ord('C') - ord('A'), 73: ord('K') - ord('A')   # OCK
    }
    
    # Track forced residues by (class_id, residue) -> key_value
    forced_residues = {}
    anchor_collisions = 0
    illegal_passthrough = False
    option_a_ok = True
    
    # Process each anchor position
    for anchor_idx, expected_pt in anchors.items():
        # For NA-only permutations, anchors are NOT in the permutation domain
        # They remain at their original positions unchanged
        
        # Compute residue address for this anchor under multi-class schedule
        class_id, residue = compute_residue_address(anchor_idx, schedule, L_vec, phase_vec)
        
        # Solve for key value at this residue
        ct_val = ct[anchor_idx]
        key_val = solve_key_value(ct_val, expected_pt, family)
        
        # Check for illegal pass-through (K=0 for Vig/VB)
        if key_val == 0 and family in ['vigenere', 'variant_beaufort']:
            illegal_passthrough = True
            option_a_ok = False
        
        # Create residue key
        residue_key = (class_id, residue)
        
        # Check for collision
        if residue_key in forced_residues:
            if forced_residues[residue_key] != key_val:
                anchor_collisions += 1
                option_a_ok = False
        else:
            forced_residues[residue_key] = key_val
    
    if not option_a_ok:
        return {
            'option_a_ok': False,
            'forced_residues': len(forced_residues),
            'anchor_collisions': anchor_collisions,
            'illegal_passthrough': illegal_passthrough,
            'tail_forced': False,
            'implied_tail': ''
        }
    
    # Check tail coverage (positions 75-96)
    tail_indices = list(range(75, 97))
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
        
        # Compute residue address needed for decryption at destination position
        class_id, residue = compute_residue_address(dst_idx, schedule, L_vec, phase_vec)
        residue_key = (class_id, residue)
        
        if residue_key not in forced_residues:
            tail_forced = False
            implied_tail.append('_')  # Unforced position
        else:
            # Decrypt this tail position
            ct_val = ct[tail_idx]
            key_val = forced_residues[residue_key]
            pt_val = decrypt_letter(ct_val, key_val, family)
            implied_tail.append(chr(pt_val + ord('A')))
    
    return {
        'option_a_ok': True,
        'forced_residues': len(forced_residues),
        'anchor_collisions': anchor_collisions,
        'illegal_passthrough': illegal_passthrough,
        'tail_forced': tail_forced,
        'implied_tail': ''.join(implied_tail)
    }

def main():
    parser = argparse.ArgumentParser(description='Anchors + multi-class tail forcing scan')
    parser.add_argument('--ct', required=True, help='Path to ciphertext file')
    parser.add_argument('--perms_dir', required=True, help='Directory with permutation JSON files')
    parser.add_argument('--policy', required=True, help='Path to policy JSON')
    parser.add_argument('--out', required=True, help='Output directory')
    parser.add_argument('--schedules', default='c6a,c6b', help='Multi-class schedules (c6a|c6b)')
    parser.add_argument('--families', default='vigenere,beaufort,variant_beaufort', help='Cipher families')
    
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
    
    # Parse families and schedules
    families = args.families.split(',')
    schedules = args.schedules.split(',')
    
    # Define test grid (keeping it tractable - start small!)
    L_k_values = [12, 16]  # Reduced from [12, 16, 20]
    phase_k_values = [0, 1]  # Reduced from [0, 1, 2]
    
    # Results collection
    results = []
    
    print(f"\n🔬 Running anchors + multi-class forcing scan...")
    print(f"   Schedules: {schedules}")
    print(f"   Families: {families}")
    print(f"   L_k values: {L_k_values}")
    print(f"   phase_k values: {phase_k_values}")
    print(f"   Routes: {len(permutations)}")
    
    total_tests = 0
    test_count = 0
    
    # Test each combination
    for route_id, na_indices, order, perm_file in permutations:
        for family in families:
            for schedule in schedules:
                # Generate all combinations of L_k and phase_k for 6 classes
                for L_combo in itertools.product(L_k_values, repeat=6):
                    for phase_combo in itertools.product(phase_k_values, repeat=6):
                        # Only test if phases are valid (phase_k < L_k for each class)
                        valid = all(phase_combo[k] < L_combo[k] for k in range(6))
                        if not valid:
                            continue
                        
                        total_tests += 1
                        test_count += 1
                        
                        if test_count % 100 == 0:
                            print(f"   Progress: {test_count} tests...")
                        
                        result = test_multiclass_forcing(ct, na_indices, order, route_id, 
                                                       family, schedule, L_combo, phase_combo)
                        
                        # Record result
                        row = {
                            'route_id': route_id,
                            'family': family,
                            'schedule': schedule,
                            'L_vec': str(L_combo),
                            'phase_vec': str(phase_combo),
                            'option_a_ok': result['option_a_ok'],
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
        fieldnames = ['route_id', 'family', 'schedule', 'L_vec', 'phase_vec', 
                      'option_a_ok', 'forced_residues', 'tail_forced', 'implied_tail', 
                      'anchor_collisions', 'illegal_passthrough']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"📄 Results written to {csv_file}")
    
    # Generate summary statistics
    option_a_ok_results = [r for r in results if r['option_a_ok']]
    tail_forced_results = [r for r in option_a_ok_results if r['tail_forced']]
    
    print(f"\n📊 Summary:")
    print(f"   Total tests: {len(results)}")
    print(f"   Option-A feasible: {len(option_a_ok_results)}")
    print(f"   Tail forced: {len(tail_forced_results)}")
    
    if tail_forced_results:
        # Check tail consistency
        unique_tails = set(r['implied_tail'] for r in tail_forced_results if r['implied_tail'])
        print(f"   Unique tail strings: {len(unique_tails)}")
        for tail in unique_tails:
            count = sum(1 for r in tail_forced_results if r['implied_tail'] == tail)
            print(f"     '{tail}': {count} models")
            
            # Show representative examples
            if count <= 3:
                examples = [r for r in tail_forced_results if r['implied_tail'] == tail]
                for ex in examples:
                    print(f"       {ex['route_id']} / {ex['family']} / {ex['schedule']}")
    
    return csv_file

if __name__ == '__main__':
    main()