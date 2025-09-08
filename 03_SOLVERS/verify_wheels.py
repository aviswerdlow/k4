#!/usr/bin/env python3
"""
Verify that the solved wheels correctly reproduce the plaintext.
"""

import json
from pathlib import Path


def letter_to_num(letter: str) -> int:
    """Convert A-Z to 0-25."""
    return ord(letter) - ord('A')


def num_to_letter(num: int) -> str:
    """Convert 0-25 to A-Z."""
    return chr(num + ord('A'))


def compute_class(i: int) -> int:
    """Compute class for index i using the 1989 formula."""
    return (i % 2) * 3 + (i % 3)


def decrypt_cell(c_val: int, k_val: int, family: str) -> int:
    """Apply family-specific decrypt rule."""
    if family == 'vigenere':
        return (c_val - k_val) % 26
    elif family == 'beaufort':
        return (k_val - c_val) % 26
    elif family == 'variant_beaufort':
        return (c_val + k_val) % 26
    else:
        raise ValueError(f"Unknown family: {family}")


def main():
    """Verify the wheel solution."""
    # Load wheels
    with open('wheels_solution.json', 'r') as f:
        wheels = json.load(f)
    
    # Load CT and PT
    with open('02_DATA/ciphertext_97.txt', 'r') as f:
        ciphertext = f.read().strip()
    
    with open('01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt', 'r') as f:
        expected_pt = f.read().strip()
    
    # Decrypt using wheels
    derived_pt = []
    errors = []
    
    for i in range(97):
        c_val = letter_to_num(ciphertext[i])
        class_id = compute_class(i)
        
        # Get wheel config
        config = wheels[str(class_id)]  # JSON keys are strings
        family = config['family']
        L = config['L']
        phase = config['phase']
        residues = config['residues']
        
        # Get K from wheel
        slot = (i - phase) % L
        k_val = residues[slot]
        
        # Decrypt
        p_val = decrypt_cell(c_val, k_val, family)
        p_letter = num_to_letter(p_val)
        derived_pt.append(p_letter)
        
        # Check match
        if p_letter != expected_pt[i]:
            errors.append(f"Position {i}: expected {expected_pt[i]}, got {p_letter}")
    
    derived_pt_str = ''.join(derived_pt)
    
    print(f"Expected: {expected_pt[:50]}...")
    print(f"Derived:  {derived_pt_str[:50]}...")
    
    if derived_pt_str == expected_pt:
        print("\n✅ SUCCESS: Wheels correctly reproduce the plaintext!")
    else:
        print(f"\n❌ FAILURE: {len(errors)} mismatches")
        for err in errors[:10]:
            print(f"  {err}")
    
    return derived_pt_str == expected_pt


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)