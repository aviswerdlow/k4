#!/usr/bin/env python3
"""Quick test of first few P74 letters to verify discrimination"""

import sys
sys.path.append('.')
from p74_final_corrected import *

def test_quick_letters():
    """Test first few letters to see discrimination pattern"""
    
    # Load data
    calibration_data = load_calibration_data()
    
    with open("../../../results/GRID_ONLY/cand_005/plaintext_97.txt", 'r') as f:
        base_plaintext = f.read().strip()
    
    # Test first 5 letters
    letters = ['T', 'S', 'A', 'I', 'O']
    
    for letter in letters:
        print(f"\n=== Testing P[74]='{letter}' ===")
        
        # Generate plaintext candidate
        plaintext = base_plaintext[:74] + letter + base_plaintext[75:]
        
        # Test AND gate
        gate_result = evaluate_and_gate(plaintext, calibration_data)
        
        print(f"Flint v2: {'✅ PASS' if gate_result['flint_v2']['pass'] else '❌ FAIL'}")
        print(f"Generic: {'✅ PASS' if gate_result['generic']['pass'] else '❌ FAIL'}")
        print(f"  Perplexity: {gate_result['generic']['perplexity_percentile']:.1f}% ≥ 99.0%")
        print(f"  POS score: {gate_result['generic']['pos_score']:.3f} ≥ 0.6")
        print(f"AND Gate: {'✅ PASS' if gate_result['pass'] else '❌ FAIL'}")
        print(f"Accepted by: {gate_result['accepted_by']}")

if __name__ == '__main__':
    test_quick_letters()