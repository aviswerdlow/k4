#!/usr/bin/env python3
"""
Debug why F1 v2 isn't catching Option-A violations
"""

import sys
sys.path.append('f1_anchor_search')

from f1_anchor_search_v2 import AnchorSearcherV2

def debug_option_a():
    """Test if Option-A is being caught"""
    searcher = AnchorSearcherV2()
    
    # Test TRUE@8 with L=11 phase=0
    result = searcher.test_placement("TRUE", 8, L=11, phase=0)
    
    print(f"Testing TRUE@8 L=11 phase=0")
    print(f"Rejected: {result.rejected}")
    print(f"Reject reasons: {result.reject_reasons}")
    print(f"Gains: {result.gains}")
    print()
    
    # Manually check position 10
    ciphertext = searcher.ciphertext
    print(f"Position 10:")
    print(f"  Ciphertext: {ciphertext[10]}")
    print(f"  Plaintext: U")
    print(f"  Class: {searcher.compute_class(10)}")
    print(f"  Family: {searcher.family_by_class[searcher.compute_class(10)]}")
    
    c_val = ord(ciphertext[10]) - ord('A')
    p_val = ord('U') - ord('A')
    family = searcher.family_by_class[searcher.compute_class(10)]
    k_req = searcher.compute_residue(c_val, p_val, family)
    print(f"  K required: {k_req}")
    
    if family in ['vigenere', 'variant-beaufort'] and k_req == 0:
        print(f"  OPTION-A VIOLATION!")
    
    # Test with different phase values
    print("\nTesting different phases:")
    for phase in range(11):
        result = searcher.test_placement("TRUE", 8, L=11, phase=phase)
        if not result.rejected:
            print(f"  Phase {phase}: ACCEPTED (gains={result.gains})")
        else:
            if 'optionA' in str(result.reject_reasons):
                print(f"  Phase {phase}: Option-A violation")
            else:
                print(f"  Phase {phase}: {result.reject_reasons[0] if result.reject_reasons else 'unknown'}")

if __name__ == "__main__":
    debug_option_a()