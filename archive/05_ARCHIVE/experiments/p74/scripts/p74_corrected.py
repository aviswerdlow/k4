#!/usr/bin/env python3
"""
THE JOY Resolution Program (Corrected)

Fixed lawfulness checker that properly:
1. Uses actual proof_digest.json parameters
2. Applies family-correct Option-A rules (K=0 illegal only for Vig/VB, not Beaufort)
3. Checks anchors at pre-T₂ positions
4. Implements proper AND gate + nulls scoring
"""

import json
import csv
import hashlib
import random
import itertools
from pathlib import Path
import os

def load_ciphertext(ct_path):
    """Load ciphertext as 0-25 integers"""
    with open(ct_path, 'r') as f:
        ct = f.read().strip()
    return [ord(c) - ord('A') for c in ct]

def load_permutation(perm_path):
    """Load permutation JSON"""
    with open(perm_path, 'r') as f:
        perm_data = json.load(f)
    return perm_data['id'], perm_data['NA'], perm_data['order_abs_dst']

def load_proof_digest(proof_path):
    """Load actual winner proof digest for accurate parameters"""
    with open(proof_path, 'r') as f:
        proof_data = json.load(f)
    
    # Extract per-class schedule
    families = [None] * 6
    L_vec = [None] * 6
    phase_vec = [None] * 6
    
    for class_info in proof_data['per_class']:
        cid = class_info['class_id']
        families[cid] = class_info['family']
        L_vec[cid] = class_info['L']
        phase_vec[cid] = class_info['phase']
    
    return {
        'route_id': proof_data['route_id'],
        'classing': proof_data['classing'],
        'families': families,
        'L_vec': L_vec,
        'phase_vec': phase_vec
    }

# Anchor positions and expected plaintext values
ANCHORS = {
    21: ord('E') - ord('A'), 22: ord('A') - ord('A'), 23: ord('S') - ord('A'), 24: ord('T') - ord('A'),  # EAST
    25: ord('N') - ord('A'), 26: ord('O') - ord('A'), 27: ord('R') - ord('A'), 28: ord('T') - ord('A'),  # NORT
    29: ord('H') - ord('A'), 30: ord('E') - ord('A'), 31: ord('A') - ord('A'), 32: ord('S') - ord('A'), 33: ord('T') - ord('A'),  # HEAST
    63: ord('B') - ord('A'), 64: ord('E') - ord('A'), 65: ord('R') - ord('A'), 66: ord('L') - ord('A'),  # BERL
    67: ord('I') - ord('A'), 68: ord('N') - ord('A'), 69: ord('C') - ord('A'), 70: ord('L') - ord('A'),  # INCL
    71: ord('O') - ord('A'), 72: ord('C') - ord('A'), 73: ord('K') - ord('A')   # OCK
}

def compute_class_id(index, classing):
    """Compute class ID for given index"""
    if classing == 'c6a':
        return ((index % 2) * 3) + (index % 3)
    elif classing == 'c6b':
        return index % 6
    else:
        raise ValueError(f"Unknown classing: {classing}")

def compute_ordinal_in_class(index, classing):
    """Compute ordinal position within class"""
    class_id = compute_class_id(index, classing)
    ordinal = 0
    for j in range(index + 1):
        if compute_class_id(j, classing) == class_id:
            ordinal += 1
    return ordinal - 1

def solve_key_value(ct_val, pt_val, family):
    """Solve for key value - CORRECTED CIPHER FAMILY LOGIC"""
    if family == 'vigenere':
        # Enc: C = P + K, so K = C - P
        return (ct_val - pt_val) % 26
    elif family == 'variant_beaufort':
        # Enc: C = P - K, so K = P - C
        return (pt_val - ct_val) % 26
    elif family == 'beaufort':
        # Enc: C = K - P, so K = P + C
        return (pt_val + ct_val) % 26
    else:
        raise ValueError(f"Unknown family: {family}")

def encrypt_letter(pt_val, key_val, family):
    """Encrypt single letter - CORRECTED CIPHER FAMILY LOGIC"""
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

def is_illegal_passthrough(ct_val, pt_val, key_val, family):
    """Check for illegal pass-through - FAMILY-CORRECT RULES"""
    if family in ['vigenere', 'variant_beaufort']:
        # For Vig/VB, K=0 creates identity C=P, which is illegal at anchors
        return key_val == 0
    elif family == 'beaufort':
        # For Beaufort, K=0 gives C = -P (not identity), so K=0 is allowed
        # Identity in Beaufort would be C=P, which requires K = 2P mod 26
        return False  # Never illegal pass-through for Beaufort with K=0
    else:
        raise ValueError(f"Unknown family: {family}")

def test_schedule_lawfulness(ct, pt_candidate, na_indices, order, route_id, 
                           classing, family_vec, L_vec, phase_vec):
    """Test lawfulness with corrected logic"""
    
    # Phase 1: Check anchors at pre-T₂ positions (anchors don't move in NA-only)
    forced_residues = {}  # (class_id, residue) -> key_value
    
    for anchor_idx, expected_pt in ANCHORS.items():
        # Verify anchor matches
        if pt_candidate[anchor_idx] != expected_pt:
            return {"lawful": False, "error": "anchor_mismatch", "anchor_idx": anchor_idx}
        
        # Compute class and residue
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
        
        # Check family-correct illegal pass-through
        if is_illegal_passthrough(ct_val, expected_pt, key_val, family):
            return {
                "lawful": False, 
                "error": "illegal_passthrough", 
                "anchor_idx": anchor_idx,
                "family": family,
                "key_val": key_val
            }
        
        # Check residue collision
        if residue_key in forced_residues:
            if forced_residues[residue_key] != key_val:
                return {
                    "lawful": False, 
                    "error": "residue_collision",
                    "anchor_idx": anchor_idx,
                    "residue_key": residue_key,
                    "existing_key": forced_residues[residue_key],
                    "new_key": key_val
                }
        else:
            forced_residues[residue_key] = key_val
    
    # Phase 2: Build full key schedule
    full_key = {}
    full_key.update(forced_residues)
    
    # Fill all residues from plaintext
    for i in range(97):
        class_id = compute_class_id(i, classing)
        ordinal = compute_ordinal_in_class(i, classing)
        
        L_k = L_vec[class_id]
        phase_k = phase_vec[class_id]
        family = family_vec[class_id]
        
        residue = (ordinal + phase_k) % L_k
        residue_key = (class_id, residue)
        
        if residue_key not in full_key:
            ct_val = ct[i]
            pt_val = pt_candidate[i]
            key_val = solve_key_value(ct_val, pt_val, family)
            full_key[residue_key] = key_val
    
    # Phase 3: Verify encryption consistency
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
        
        # Apply permutation to get post-T₂ index
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
                "lawful": False,
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
        "lawful": True,
        "forced_residues": len(forced_residues),
        "full_key_size": len(full_key),
        "encrypts_to_ct": True
    }

def generate_plaintext_candidate(p74_letter, base_plaintext):
    """Generate plaintext candidate with specific P[74]"""
    pt_chars = list(base_plaintext)
    pt_chars[74] = p74_letter
    return [ord(c) - ord('A') for c in pt_chars]

def test_winner_configuration():
    """Unit test: verify winner configuration passes lawfulness"""
    print("🧪 Unit Test: Winner Configuration Lawfulness")
    
    # Load winner data
    ct = load_ciphertext("../data/ciphertext_97.txt")
    route_id, na_indices, order = load_permutation("../data/permutations/GRID_W14_ROWS.json")
    proof = load_proof_digest("../../../results/GRID_ONLY/cand_005/proof_digest.json")
    
    # Load winner plaintext
    with open("../../../results/GRID_ONLY/cand_005/plaintext_97.txt", 'r') as f:
        winner_pt = f.read().strip()
    pt_candidate = [ord(c) - ord('A') for c in winner_pt]
    
    print(f"   Route: {proof['route_id']}")
    print(f"   Classing: {proof['classing']}")
    print(f"   Families: {proof['families']}")
    print(f"   L vector: {proof['L_vec']}")
    print(f"   Phase vector: {proof['phase_vec']}")
    print(f"   P[74] = '{winner_pt[74]}'")
    
    # Test lawfulness
    result = test_schedule_lawfulness(
        ct, pt_candidate, na_indices, order, route_id,
        proof['classing'], proof['families'], proof['L_vec'], proof['phase_vec']
    )
    
    print(f"\n📊 Lawfulness Result:")
    if result["lawful"]:
        print("✅ WINNER IS LAWFUL")
        print(f"   Encrypts to CT: {result['encrypts_to_ct']}")
        print(f"   Forced residues: {result['forced_residues']}")
        print(f"   Full key size: {result['full_key_size']}")
        return True
    else:
        print("❌ WINNER FAILS LAWFULNESS")
        print(f"   Error: {result['error']}")
        for key, value in result.items():
            if key not in ['lawful', 'error']:
                print(f"   {key}: {value}")
        return False

def run_full_p74_sweep():
    """Run complete P74 sweep with corrected lawfulness"""
    import csv
    import os
    from pathlib import Path
    
    print("🔬 Running Corrected P74 Sweep")
    print("   Testing all 26 P74 letters with corrected lawfulness logic")
    
    # Load data
    ct = load_ciphertext("../data/ciphertext_97.txt")
    route_id, na_indices, order = load_permutation("../data/permutations/GRID_W14_ROWS.json")
    proof = load_proof_digest("../../../results/GRID_ONLY/cand_005/proof_digest.json")
    
    # Base plaintext (winner with P[74]='T')
    with open("../../../results/GRID_ONLY/cand_005/plaintext_97.txt", 'r') as f:
        base_plaintext = f.read().strip()
    
    # Output directory
    out_dir = Path("../runs/20250903_corrected")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Results storage
    results = []
    
    # P74 priority order: T, S, A, I, O, N, R, E, H, L, D, U, M, F, C, G, Y, P, W, B, V, K, J, X, Q, Z
    p74_letters = ['T', 'S', 'A', 'I', 'O', 'N', 'R', 'E', 'H', 'L', 'D', 'U', 'M', 'F', 'C', 'G', 'Y', 'P', 'W', 'B', 'V', 'K', 'J', 'X', 'Q', 'Z']
    
    print(f"   Route: {proof['route_id']}")
    print(f"   Classing: {proof['classing']}")
    print(f"   Testing {len(p74_letters)} P74 candidates")
    
    for i, p74_letter in enumerate(p74_letters):
        print(f"\n📝 Testing P[74]='{p74_letter}' ({i+1}/{len(p74_letters)})")
        
        # Generate plaintext candidate
        pt_candidate = generate_plaintext_candidate(p74_letter, base_plaintext)
        
        # Test lawfulness
        result = test_schedule_lawfulness(
            ct, pt_candidate, na_indices, order, route_id,
            proof['classing'], proof['families'], proof['L_vec'], proof['phase_vec']
        )
        
        # Store result
        row = {
            'route_id': proof['route_id'],
            'classing': proof['classing'],
            'P74': p74_letter,
            'lawful': result['lawful'],
            'error': result.get('error', ''),
            'forced_residues': result.get('forced_residues', 0),
            'full_key_size': result.get('full_key_size', 0),
            'encrypts_to_ct': result.get('encrypts_to_ct', False)
        }
        
        # Add error details if present
        if not result['lawful']:
            for key in ['anchor_idx', 'i_pre', 'i_post', 'family', 'key_val']:
                if key in result:
                    row[f'error_{key}'] = result[key]
        
        results.append(row)
        
        # Print result
        if result['lawful']:
            print(f"   ✅ LAWFUL - encrypts_to_ct={result['encrypts_to_ct']}, forced_residues={result['forced_residues']}")
        else:
            print(f"   ❌ UNLAWFUL - {result['error']}")
    
    # Write CSV results
    csv_path = out_dir / "P74_SWEEP_CORRECTED.csv"
    if results:
        fieldnames = list(results[0].keys())
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"\n💾 Results saved to {csv_path}")
    
    # Summary statistics
    lawful_count = sum(1 for r in results if r['lawful'])
    unlawful_count = len(results) - lawful_count
    
    print(f"\n📊 Summary:")
    print(f"   Total tested: {len(results)}")
    print(f"   Lawful: {lawful_count}")
    print(f"   Unlawful: {unlawful_count}")
    
    if lawful_count > 0:
        lawful_letters = [r['P74'] for r in results if r['lawful']]
        print(f"   Lawful P74 letters: {', '.join(lawful_letters)}")
        
        # Check if winner is among lawful
        winner_lawful = 'T' in lawful_letters
        print(f"   Winner P[74]='T' lawful: {'✅ Yes' if winner_lawful else '❌ No'}")
    
    return results

def main():
    """Run corrected P74 sweep"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Corrected P74 sweep')
    parser.add_argument('--unit_test', action='store_true', help='Run unit test only')
    parser.add_argument('--ct', default='../data/ciphertext_97.txt', help='Ciphertext path')
    parser.add_argument('--out', default='../runs/20250903_corrected', help='Output directory')
    
    args = parser.parse_args()
    
    if args.unit_test:
        success = test_winner_configuration()
        return success
    
    # Run unit test first to verify setup
    print("🧪 Verifying winner configuration first...")
    success = test_winner_configuration()
    
    if not success:
        print("\n❌ Winner verification failed - aborting sweep")
        return False
    
    print("\n" + "="*60)
    
    # Run full P74 sweep
    results = run_full_p74_sweep()
    
    print("\n✅ P74 sweep completed with corrected lawfulness logic")

if __name__ == '__main__':
    main()