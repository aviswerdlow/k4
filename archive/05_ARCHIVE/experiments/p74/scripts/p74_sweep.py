#!/usr/bin/env python3
"""
THE JOY Resolution Program (P74 Sweep)

Determines if P[74]='T' is effectively forced under published rails and gates,
or if viable alternatives exist that pass the head-only AND gate plus nulls.
"""

import json
import csv
import argparse
import hashlib
import random
import itertools
from pathlib import Path
from datetime import datetime
import os

# Anchor positions and expected plaintext values
ANCHORS = {
    21: ord('E') - ord('A'), 22: ord('A') - ord('A'), 23: ord('S') - ord('A'), 24: ord('T') - ord('A'),  # EAST
    25: ord('N') - ord('A'), 26: ord('O') - ord('A'), 27: ord('R') - ord('A'), 28: ord('T') - ord('A'),  # NORT
    29: ord('H') - ord('A'), 30: ord('E') - ord('A'), 31: ord('A') - ord('A'), 32: ord('S') - ord('A'), 33: ord('T') - ord('A'),  # HEAST
    63: ord('B') - ord('A'), 64: ord('E') - ord('A'), 65: ord('R') - ord('A'), 66: ord('L') - ord('A'),  # BERL
    67: ord('I') - ord('A'), 68: ord('N') - ord('A'), 69: ord('C') - ord('A'), 70: ord('L') - ord('A'),  # INCL
    71: ord('O') - ord('A'), 72: ord('C') - ord('A'), 73: ord('K') - ord('A')   # OCK
}

def load_ciphertext(ct_path):
    """Load ciphertext as A..Z string converted to 0-25 integers"""
    with open(ct_path, 'r') as f:
        ct = f.read().strip()
    return [ord(c) - ord('A') for c in ct]

def load_permutation(perm_path):
    """Load permutation JSON - assumes NA-only (anchors fixed by exclusion)"""
    with open(perm_path, 'r') as f:
        perm_data = json.load(f)
    
    route_id = perm_data['id']
    na_indices = perm_data['NA']
    order = perm_data['order_abs_dst']
    
    return route_id, na_indices, order

def compute_class_id(index, classing):
    """Compute class ID for given index under c6a or c6b"""
    if classing == 'c6a':
        return ((index % 2) * 3) + (index % 3)
    elif classing == 'c6b':
        return index % 6
    else:
        raise ValueError(f"Unknown classing: {classing}")

def compute_ordinal_in_class(index, classing):
    """Compute ordinal position within class for given index"""
    class_id = compute_class_id(index, classing)
    # Count indices j <= index with same class_id
    ordinal = 0
    for j in range(index + 1):
        if compute_class_id(j, classing) == class_id:
            ordinal += 1
    return ordinal - 1  # 0-indexed

def solve_key_value(ct_val, pt_val, family):
    """Solve for key value given C, P, and cipher family"""
    if family == 'vigenere':
        # P = C - K, so K = C - P
        return (ct_val - pt_val) % 26
    elif family == 'variant_beaufort':
        # P = C + K, so K = P - C
        return (pt_val - ct_val) % 26
    elif family == 'beaufort':
        # P = K - C, so K = P + C
        return (pt_val + ct_val) % 26
    else:
        raise ValueError(f"Unknown family: {family}")

def encrypt_letter(pt_val, key_val, family):
    """Encrypt single letter given P, K, and family"""
    if family == 'vigenere':
        # C = P + K
        return (pt_val + key_val) % 26
    elif family == 'variant_beaufort':
        # C = P - K
        return (pt_val - key_val) % 26
    elif family == 'beaufort':
        # C = K - P
        return (key_val - pt_val) % 26
    else:
        raise ValueError(f"Unknown family: {family}")

def test_schedule_feasibility(ct, pt_candidate, na_indices, order, route_id, 
                            classing, family_vec, L_vec, phase_vec):
    """Test if candidate plaintext is lawful under given schedule parameters"""
    
    # Build forced residue map from anchors
    forced_residues = {}  # (class_id, residue) -> key_value
    
    # Process anchors first
    for anchor_idx, expected_pt in ANCHORS.items():
        if pt_candidate[anchor_idx] != expected_pt:
            return {"feasible": False, "error": "anchor_mismatch", "anchor_idx": anchor_idx}
        
        class_id = compute_class_id(anchor_idx, classing)
        ordinal = compute_ordinal_in_class(anchor_idx, classing)
        
        L_k = L_vec[class_id]
        phase_k = phase_vec[class_id]
        family = family_vec[class_id]
        
        residue = (ordinal + phase_k) % L_k
        residue_key = (class_id, residue)
        
        # Solve for key value
        ct_val = ct[anchor_idx]
        key_val = solve_key_value(ct_val, expected_pt, family)
        
        # Check illegal pass-through
        if key_val == 0 and family in ['vigenere', 'variant_beaufort']:
            return {"feasible": False, "error": "illegal_passthrough", "anchor_idx": anchor_idx}
        
        # Check collision
        if residue_key in forced_residues:
            if forced_residues[residue_key] != key_val:
                return {"feasible": False, "error": "anchor_collision", 
                       "anchor_idx": anchor_idx, "residue_key": residue_key}
        else:
            forced_residues[residue_key] = key_val
    
    # Now build full key schedule and test encryption
    full_key = {}  # (class_id, residue) -> key_value
    full_key.update(forced_residues)
    
    # Fill in all residues from full plaintext
    for i in range(97):
        class_id = compute_class_id(i, classing)
        ordinal = compute_ordinal_in_class(i, classing)
        
        L_k = L_vec[class_id]
        phase_k = phase_vec[class_id]
        family = family_vec[class_id]
        
        residue = (ordinal + phase_k) % L_k
        residue_key = (class_id, residue)
        
        if residue_key not in full_key:
            # Need to solve from plaintext at this position
            ct_val = ct[i]
            pt_val = pt_candidate[i]
            key_val = solve_key_value(ct_val, pt_val, family)
            full_key[residue_key] = key_val
    
    # Now verify encryption consistency
    for i in range(97):
        class_id = compute_class_id(i, classing)
        ordinal = compute_ordinal_in_class(i, classing)
        
        L_k = L_vec[class_id]
        phase_k = phase_vec[class_id] 
        family = family_vec[class_id]
        
        residue = (ordinal + phase_k) % L_k
        residue_key = (class_id, residue)
        
        key_val = full_key[residue_key]
        pt_val = pt_candidate[i]
        
        # Apply permutation to get post-T2 index
        if i in na_indices:
            na_pos = na_indices.index(i)
            post_t2_idx = order[na_pos]
        else:
            post_t2_idx = i
        
        # Encrypt and compare
        expected_ct = encrypt_letter(pt_val, key_val, family)
        actual_ct = ct[post_t2_idx]
        
        if expected_ct != actual_ct:
            return {
                "feasible": False, 
                "error": "encrypt_mismatch",
                "i_pre": i,
                "i_post": post_t2_idx,
                "class_id": class_id,
                "family": family,
                "L": L_k,
                "phase": phase_k,
                "r": residue,
                "K": key_val,
                "P_pre": pt_val,
                "C_expected_post": expected_ct,
                "C_built_post": actual_ct
            }
    
    return {
        "feasible": True,
        "forced_residues": len(forced_residues),
        "full_key_size": len(full_key),
        "encrypts_to_ct": True
    }

def find_feasible_schedule(ct, pt_candidate, na_indices, order, route_id, classing):
    """Find feasible schedule using targeted search based on known winner structure"""
    
    # Use actual winner parameters from proof_digest.json
    known_winner_schedule = {
        'GRID_W14_ROWS': {
            'c6a': {
                'families': ['vigenere', 'vigenere', 'beaufort', 'vigenere', 'vigenere', 'beaufort'],
                'L_vec': [17, 16, 16, 16, 19, 20],
                'phase_vec': [0, 0, 0, 0, 0, 0]
            }
        },
        'GRID_W10_NW': {
            'c6a': {
                'families': ['vigenere', 'vigenere', 'beaufort', 'vigenere', 'vigenere', 'beaufort'],
                'L_vec': [18, 16, 17, 16, 18, 19], 
                'phase_vec': [0, 0, 0, 0, 0, 0]
            }
        }
    }
    
    # Get baseline parameters
    if route_id in known_winner_schedule and classing in known_winner_schedule[route_id]:
        baseline = known_winner_schedule[route_id][classing]
        winner_families = baseline['families']
        winner_L = baseline['L_vec']
        base_phases = baseline['phase_vec']
    else:
        # Default fallback
        winner_families = ['vigenere'] * 6
        winner_L = [22] * 6
        base_phases = [0] * 6
    
    # Shell 1: Test baseline with small phase variations (faster)
    phase_variations = [
        base_phases,  # Exact baseline
        [0, 0, 0, 0, 0, 1],  # Single phase shift
        [1, 0, 0, 0, 0, 0],  # Different single shift
        [0, 1, 0, 1, 0, 1],  # Alternating pattern
    ]
    
    for phase_vec in phase_variations:
        if all(phase_vec[k] < winner_L[k] for k in range(6)):
            result = test_schedule_feasibility(
                ct, pt_candidate, na_indices, order, route_id,
                classing, winner_families, winner_L, phase_vec
            )
            if result["feasible"]:
                return {
                    "found": True,
                    "family_vec": winner_families,
                    "L_vec": winner_L,
                    "phase_vec": phase_vec,
                    "shell": 1,
                    "result": result
                }
    
    # Shell 2: Limited L variations with optimized phases
    L_variations = [
        [20, 20, 20, 20, 20, 20],
        [22, 22, 22, 22, 22, 22],
        [16, 20, 16, 20, 16, 20],  # Mixed periods
    ]
    
    for L_vec in L_variations:
        # Test only a few promising phase patterns
        for phase_pattern in [[0]*6, [1, 0, 1, 0, 1, 0]]:
            if all(phase_pattern[k] < L_vec[k] for k in range(6)):
                result = test_schedule_feasibility(
                    ct, pt_candidate, na_indices, order, route_id,
                    classing, winner_families, L_vec, phase_pattern
                )
                if result["feasible"]:
                    return {
                        "found": True,
                        "family_vec": winner_families,
                        "L_vec": L_vec,
                        "phase_vec": phase_pattern,
                        "shell": 2,
                        "result": result
                    }
    
    return {"found": False, "shells_tried": 2}

def generate_plaintext_candidate(p74_letter):
    """Generate 97-char plaintext with specific P[74] and known anchors"""
    # Start with known winner plaintext structure
    base_pt = "WECANSEETHETEXTISCODEEASTNORTHEASTWESETTHECOURSETRUEREADTHENSEEBERLINCLOCKTHEJOYOFANANGLEISTHEARC"
    
    # Convert to list for modification
    pt_chars = list(base_pt)
    
    # Set P[74] to the test letter
    pt_chars[74] = p74_letter
    
    # Convert to integer array
    return [ord(c) - ord('A') for c in pt_chars]

def main():
    parser = argparse.ArgumentParser(description='P74 sweep analysis')
    parser.add_argument('--ct', required=True, help='Path to ciphertext file')
    parser.add_argument('--perms_dir', required=True, help='Directory with permutation files')
    parser.add_argument('--policy', required=True, help='Path to policy file')
    parser.add_argument('--out', required=True, help='Output directory')
    parser.add_argument('--routes', default='GRID_W14_ROWS,GRID_W10_NW', help='Routes to test')
    
    args = parser.parse_args()
    
    os.makedirs(args.out, exist_ok=True)
    
    # Load data
    ct = load_ciphertext(args.ct)
    
    # Load permutations
    routes = args.routes.split(',')
    permutations = {}
    
    for route_id in routes:
        perm_file = Path(args.perms_dir) / f"{route_id}.json"
        if perm_file.exists():
            route_id, na_indices, order = load_permutation(perm_file)
            permutations[route_id] = (na_indices, order)
            print(f"✅ Loaded {route_id}")
        else:
            print(f"❌ Missing {perm_file}")
    
    # P74 sweep - prioritize likely English continuations
    p74_priority = ['T', 'S', 'A', 'I', 'O', 'N', 'R', 'E', 'H', 'L', 'D', 'U', 'M', 'F', 'C', 'G', 'Y', 'P', 'W', 'B', 'V', 'K', 'J', 'X', 'Q', 'Z']
    
    results = []
    
    print(f"\n🔬 Running P74 sweep analysis...")
    print(f"   Routes: {list(permutations.keys())}")
    print(f"   Classings: c6a, c6b")
    print(f"   P74 priority: {p74_priority[:10]}...")
    
    viable_found = False
    
    for route_id, (na_indices, order) in permutations.items():
        for classing in ['c6a', 'c6b']:
            print(f"\n📋 Testing {route_id} / {classing}")
            
            for p74_letter in p74_priority:
                print(f"   Testing P[74]={p74_letter}...", end="")
                
                # Generate candidate plaintext
                pt_candidate = generate_plaintext_candidate(p74_letter)
                
                # Find feasible schedule
                schedule_result = find_feasible_schedule(
                    ct, pt_candidate, na_indices, order, route_id, classing
                )
                
                if schedule_result["found"]:
                    print(f" ✅ FEASIBLE (shell {schedule_result['shell']})")
                    
                    # Store result for later scoring/gating
                    row = {
                        'route_id': route_id,
                        'classing': classing,
                        'P74': p74_letter,
                        'feasible_schedules': 1,
                        'shell_found': schedule_result['shell'],
                        'family_vec': str(schedule_result['family_vec']),
                        'L_vec': str(schedule_result['L_vec']),
                        'phase_vec': str(schedule_result['phase_vec']),
                        'AND_pass': False,  # TODO: Implement full gating
                        'nulls_cov_holm': 1.0,  # TODO: Implement nulls
                        'nulls_fw_holm': 1.0,   # TODO: Implement nulls
                        'publishable': False,
                        'tail_75_96': ''.join([chr(pt_candidate[i] + ord('A')) for i in range(75, 97)])
                    }
                    results.append(row)
                    
                    if p74_letter != 'T':
                        viable_found = True
                        print(f"      🎯 Non-T candidate found: P[74]={p74_letter}")
                else:
                    print(" ❌ infeasible")
                    
                    row = {
                        'route_id': route_id,
                        'classing': classing,
                        'P74': p74_letter,
                        'feasible_schedules': 0,
                        'shell_found': None,
                        'family_vec': None,
                        'L_vec': None,
                        'phase_vec': None,
                        'AND_pass': False,
                        'nulls_cov_holm': 1.0,
                        'nulls_fw_holm': 1.0,
                        'publishable': False,
                        'tail_75_96': ''
                    }
                    results.append(row)
    
    # Write preliminary results
    csv_file = Path(args.out) / 'P74_SWEEP_SUMMARY.csv'
    with open(csv_file, 'w', newline='') as f:
        fieldnames = ['route_id', 'classing', 'P74', 'feasible_schedules', 'shell_found',
                      'family_vec', 'L_vec', 'phase_vec', 'AND_pass', 'nulls_cov_holm', 
                      'nulls_fw_holm', 'publishable', 'tail_75_96']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n📊 Preliminary Results:")
    feasible_count = sum(1 for r in results if r['feasible_schedules'] > 0)
    total_count = len(results)
    print(f"   Feasible: {feasible_count}/{total_count}")
    
    if viable_found:
        non_t_feasible = [r for r in results if r['P74'] != 'T' and r['feasible_schedules'] > 0]
        print(f"   Non-T viable candidates: {len(non_t_feasible)}")
        for r in non_t_feasible:
            print(f"     {r['route_id']}/{r['classing']}/P[74]={r['P74']}: tail={r['tail_75_96']}")
    else:
        print(f"   ✅ Only P[74]='T' shows feasible schedules")
    
    print(f"\n📄 Preliminary results: {csv_file}")
    print("   (Full AND gate + nulls scoring not yet implemented)")

if __name__ == '__main__':
    main()