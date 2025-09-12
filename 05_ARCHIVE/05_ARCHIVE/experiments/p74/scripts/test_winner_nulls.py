#!/usr/bin/env python3
"""Test winner with nulls analysis"""

import sys
sys.path.append('.')
from p74_final_corrected import *

def test_winner_with_nulls():
    """Test winner P[74]='T' with nulls to confirm publishable"""
    
    print("🧪 Testing Winner P[74]='T' with Nulls Analysis")
    print("=" * 60)
    
    # Load data
    calibration_data = load_calibration_data()
    ct = load_ciphertext("../data/ciphertext_97.txt")
    route_id, na_indices, order = load_permutation("../data/permutations/GRID_W14_ROWS.json")
    proof = load_proof_digest("../../../results/GRID_ONLY/cand_005/proof_digest.json")
    
    # Winner plaintext
    with open("../../../results/GRID_ONLY/cand_005/plaintext_97.txt", 'r') as f:
        winner_plaintext = f.read().strip()
    
    print(f"Winner: {winner_plaintext}")
    print(f"P[74] = '{winner_plaintext[74]}'")
    print(f"Tail [75,96]: {winner_plaintext[75:97]}")
    
    # Test AND gate
    gate_result = evaluate_and_gate(winner_plaintext, calibration_data)
    
    print(f"\n🔗 AND Gate: {'✅ PASS' if gate_result['pass'] else '❌ FAIL'}")
    print(f"   Accepted by: {gate_result['accepted_by']}")
    
    if gate_result['pass']:
        # Run nulls with small K for testing
        print(f"\n📊 Running nulls analysis (K=1000 for testing)...")
        
        # Simplified forced residues (would extract from lawfulness in real implementation)
        forced_residues = {}
        
        nulls_result = run_nulls_analysis(
            ct, na_indices, order, proof['classing'], proof['families'], 
            proof['L_vec'], proof['phase_vec'], forced_residues, winner_plaintext, 
            calibration_data['canonical_cuts'], K=1000
        )
        
        print(f"\n📈 Nulls Results:")
        print(f"   Coverage: {nulls_result['candidate_coverage']:.4f} (p={nulls_result['p_coverage']:.6f}, adj-p={nulls_result['adj_p_coverage']:.6f})")
        print(f"   F-words: {nulls_result['candidate_f_words']:.4f} (p={nulls_result['p_f_words']:.6f}, adj-p={nulls_result['adj_p_f_words']:.6f})")
        print(f"   Publishable: {'✅ YES' if nulls_result['publishable'] else '❌ NO'} (both adj-p < 0.01)")
        
        return nulls_result['publishable']
    
    return False

if __name__ == '__main__':
    success = test_winner_with_nulls()
    print(f"\nResult: Winner is {'publishable' if success else 'not publishable'}")