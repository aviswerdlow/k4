#!/usr/bin/env python3
"""
Debug script to test exact winner parameters
"""

import json
import sys
sys.path.append('.')
from p74_sweep import *

def test_exact_winner():
    """Test exact winner configuration to debug feasibility logic"""
    
    # Load exact winner data
    ct = load_ciphertext("../data/ciphertext_97.txt")
    route_id, na_indices, order = load_permutation("../data/permutations/GRID_W14_ROWS.json")
    
    # Exact winner plaintext
    winner_pt = "WECANSEETHETEXTISCODEEASTNORTHEASTWESETTHECOURSETRUEREADTHENSEEBERLINCLOCKTHEJOYOFANANGLEISTHEARC"
    pt_candidate = [ord(c) - ord('A') for c in winner_pt]
    
    # Exact winner parameters from proof_digest.json  
    classing = 'c6a'
    family_vec = ['vigenere', 'vigenere', 'beaufort', 'vigenere', 'vigenere', 'beaufort']
    L_vec = [17, 16, 16, 16, 19, 20]
    phase_vec = [0, 0, 0, 0, 0, 0]
    
    print(f"🧪 Testing exact winner configuration:")
    print(f"   Route: {route_id}")
    print(f"   Classing: {classing}")
    print(f"   Families: {family_vec}")
    print(f"   L vector: {L_vec}")
    print(f"   Phase vector: {phase_vec}")
    print(f"   P[74] = '{winner_pt[74]}'")
    
    # Test feasibility
    result = test_schedule_feasibility(
        ct, pt_candidate, na_indices, order, route_id,
        classing, family_vec, L_vec, phase_vec
    )
    
    print(f"\n📊 Result: {result}")
    
    if not result["feasible"]:
        print(f"❌ EXACT WINNER IS INFEASIBLE!")
        print(f"Error: {result.get('error', 'unknown')}")
        if 'anchor_idx' in result:
            print(f"Anchor index: {result['anchor_idx']}")
        if 'i_pre' in result:
            print(f"Mismatch at pre-T2 index {result['i_pre']} -> post-T2 index {result['i_post']}")
            print(f"Expected C={result['C_expected_post']}, got C={result['C_built_post']}")
    else:
        print(f"✅ Winner is feasible as expected")
        print(f"Forced residues: {result['forced_residues']}")
        print(f"Full key size: {result['full_key_size']}")

if __name__ == '__main__':
    test_exact_winner()