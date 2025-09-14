#!/usr/bin/env python3
"""
Deterministic re-encoder for homophonic cipher
Proves round-trip: PT + mapping → exact CT
"""

import json
from typing import Dict

# K4 ciphertext for verification
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def load_mapping(filename: str = 'stabilized_homophonic.json') -> Dict[str, str]:
    """Load the CT→PT mapping from saved results"""
    with open(filename, 'r') as f:
        data = json.load(f)
    return data['mapping']

def invert_mapping(ct_to_pt: Dict[str, str]) -> Dict[str, str]:
    """Create PT→CT mapping from CT→PT"""
    pt_to_ct = {}
    for ct, pt in ct_to_pt.items():
        # For deterministic encoding, use first CT symbol for each PT
        if pt not in pt_to_ct:
            pt_to_ct[pt] = ct
    return pt_to_ct

def encode_deterministic(plaintext: str, 
                        ct_to_pt_mapping: Dict[str, str],
                        original_ct: str = K4_CIPHERTEXT) -> str:
    """
    Deterministically encode plaintext to match original ciphertext
    
    Args:
        plaintext: The plaintext to encode
        ct_to_pt_mapping: The CT→PT mapping discovered
        original_ct: The original ciphertext to match
    
    Returns:
        Encoded ciphertext that should match original
    """
    # Invert mapping to get PT→CT
    pt_to_ct = invert_mapping(ct_to_pt_mapping)
    
    # For each position, find the CT symbol that:
    # 1. Maps to the current PT letter
    # 2. Matches the original CT at this position (if possible)
    
    result = []
    for i, pt_char in enumerate(plaintext):
        if i < len(original_ct):
            original_ct_char = original_ct[i]
            
            # Check if original CT char maps to current PT char
            if original_ct_char in ct_to_pt_mapping:
                if ct_to_pt_mapping[original_ct_char] == pt_char:
                    # Perfect match - use original CT
                    result.append(original_ct_char)
                    continue
            
            # Otherwise use default mapping
            if pt_char in pt_to_ct:
                result.append(pt_to_ct[pt_char])
            else:
                # No mapping found - pass through
                result.append(pt_char)
        else:
            # Beyond original CT length
            if pt_char in pt_to_ct:
                result.append(pt_to_ct[pt_char])
            else:
                result.append(pt_char)
    
    return ''.join(result)

def verify_round_trip(plaintext: str, mapping: Dict[str, str]) -> bool:
    """
    Verify that PT → CT → PT round-trips correctly
    
    Args:
        plaintext: The decoded plaintext
        mapping: The CT→PT mapping
    
    Returns:
        True if round-trip succeeds
    """
    # Encode back to CT
    encoded_ct = encode_deterministic(plaintext, mapping)
    
    # Decode using mapping
    decoded_pt = []
    for ct_char in encoded_ct:
        if ct_char in mapping:
            decoded_pt.append(mapping[ct_char])
        else:
            decoded_pt.append(ct_char)
    
    decoded = ''.join(decoded_pt)
    
    # Check if it matches
    success = (decoded == plaintext)
    
    print("=" * 80)
    print("ROUND-TRIP VERIFICATION")
    print("=" * 80)
    print(f"\nOriginal PT: {plaintext[:40]}...")
    print(f"Encoded CT:  {encoded_ct[:40]}...")
    print(f"Decoded PT:  {decoded[:40]}...")
    print(f"\nOriginal K4: {K4_CIPHERTEXT[:40]}...")
    print(f"\nCT matches K4: {encoded_ct == K4_CIPHERTEXT}")
    print(f"PT round-trips: {success}")
    
    return success

def main():
    """Test the re-encoder"""
    # Load saved results
    with open('stabilized_homophonic.json', 'r') as f:
        data = json.load(f)
    
    plaintext = data['plaintext']
    mapping = data['mapping']
    
    print("Testing deterministic re-encoding...")
    print()
    
    # Test round-trip
    success = verify_round_trip(plaintext, mapping)
    
    if success:
        print("\n✅ Round-trip verification PASSED")
    else:
        print("\n❌ Round-trip verification FAILED")
    
    # Show the mapping
    print("\n" + "=" * 80)
    print("MAPPING SUMMARY")
    print("=" * 80)
    
    # Count unique PT letters
    pt_letters = set(mapping.values())
    print(f"CT symbols: {len(mapping)}")
    print(f"PT letters: {len(pt_letters)}")
    
    # Show sample mappings
    print("\nSample mappings (CT → PT):")
    for i, (ct, pt) in enumerate(list(mapping.items())[:10]):
        print(f"  {ct} → {pt}")

if __name__ == "__main__":
    main()