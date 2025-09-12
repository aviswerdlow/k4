#!/usr/bin/env python3
"""
K4 plaintext re-deriver that handles incomplete wheels (None residues).
Shows '?' for undetermined positions.
Pure Python stdlib - no external dependencies.
"""

import json
import argparse
from typing import Dict, List, Optional

def class_function(i: int) -> int:
    """Six-track periodic classing: class(i) = ((i % 2) * 3) + (i % 3)"""
    return ((i % 2) * 3) + (i % 3)

def decrypt_vigenere(c: int, k: int) -> int:
    """Vigenère decrypt: P = C - K (mod 26)"""
    return (c - k) % 26

def decrypt_beaufort(c: int, k: int) -> int:
    """Beaufort decrypt: P = K - C (mod 26)"""
    return (k - c) % 26

def decrypt_variant_beaufort(c: int, k: int) -> int:
    """Variant-Beaufort decrypt: P = C + K (mod 26)"""
    return (c + k) % 26

def letter_to_num(letter: str) -> int:
    """Convert A=0, B=1, ..., Z=25"""
    return ord(letter.upper()) - ord('A')

def num_to_letter(num: int) -> str:
    """Convert 0=A, 1=B, ..., 25=Z"""
    return chr(num + ord('A'))

def get_wheel_slot(index: int, phase: int, period: int) -> int:
    """Calculate wheel slot for given index, phase, and period"""
    return (index - phase) % period

def decrypt_index(i: int, ct_char: str, wheels: Dict, explain: bool = False) -> str:
    """Decrypt a single index using the appropriate wheel. Returns '?' if undetermined."""
    # Get class
    cls = class_function(i)
    
    # Handle case where we have wheels in a different format
    if 'wheels' in wheels:
        wheel = wheels['wheels'][str(cls)]  # Keys are strings in our JSON
    else:
        wheel = wheels[str(cls)]
    
    # Get wheel parameters
    family = wheel['family']
    period = wheel['L']
    phase = wheel['phase']
    residues = wheel['residues']
    
    # Calculate slot
    slot = get_wheel_slot(i, phase, period)
    
    # Get key residue at this slot
    k = residues[slot]
    
    # If key residue is None, position is undetermined
    if k is None:
        if explain:
            print(f"\nIndex {i}:")
            print(f"  Class: {cls}")
            print(f"  Family: {family}")
            print(f"  Period (L): {period}")
            print(f"  Phase: {phase}")
            print(f"  Slot: {slot} = ({i} - {phase}) % {period}")
            print(f"  Key residue (K): UNDETERMINED")
            print(f"  Ciphertext (C): {ct_char}")
            print(f"  Plaintext: ? (undetermined - no wheel constraint)")
        return '?'
    
    # Get ciphertext value
    c = letter_to_num(ct_char)
    
    # Apply decrypt rule based on family
    if family == 'vigenere':
        p = decrypt_vigenere(c, k)
    elif family == 'beaufort':
        p = decrypt_beaufort(c, k)
    elif family == 'variant_beaufort':
        p = decrypt_variant_beaufort(c, k)
    else:
        raise ValueError(f"Unknown family: {family}")
    
    if explain:
        print(f"\nIndex {i}:")
        print(f"  Class: {cls}")
        print(f"  Family: {family}")
        print(f"  Period (L): {period}")
        print(f"  Phase: {phase}")
        print(f"  Slot: {slot} = ({i} - {phase}) % {period}")
        print(f"  Key residue (K): {k} ({num_to_letter(k)})")
        print(f"  Ciphertext (C): {ct_char} = {c}")
        if family == 'vigenere':
            print(f"  Decrypt: P = C - K = {c} - {k} = {p} (mod 26)")
        elif family == 'beaufort':
            print(f"  Decrypt: P = K - C = {k} - {c} = {p} (mod 26)")
        else:  # variant_beaufort
            print(f"  Decrypt: P = C + K = {c} + {k} = {p} (mod 26)")
        print(f"  Plaintext: {num_to_letter(p)}")
    
    return num_to_letter(p)

def main():
    parser = argparse.ArgumentParser(description='K4 re-deriver with gap handling')
    parser.add_argument('--ct', required=True, help='Path to ciphertext file')
    parser.add_argument('--proof', required=True, help='Path to wheels JSON')
    parser.add_argument('--out', help='Output path for plaintext')
    parser.add_argument('--explain', type=int, help='Explain derivation at index')
    parser.add_argument('--explain-range', help='Explain range (e.g., 63:74)')
    
    args = parser.parse_args()
    
    # Read ciphertext
    with open(args.ct, 'r') as f:
        ct = f.read().strip().upper()
    
    # Parse wheels
    with open(args.proof, 'r') as f:
        wheels_data = json.load(f)
    
    # If explain mode, handle single index or range
    if args.explain is not None:
        i = args.explain
        if 0 <= i < len(ct):
            decrypt_index(i, ct[i], wheels_data, explain=True)
        else:
            print(f"Index {i} out of range (0-{len(ct)-1})")
        return
    
    if args.explain_range:
        # Parse range like "63:74"
        start, end = map(int, args.explain_range.split(':'))
        for i in range(start, min(end, len(ct))):
            decrypt_index(i, ct[i], wheels_data, explain=True)
        return
    
    # Regular derivation mode
    if not args.out:
        print("Error: --out is required for derivation mode")
        return
    
    # Decrypt all letters
    plaintext = []
    undetermined_count = 0
    undetermined_indices = []
    
    for i in range(len(ct)):
        p_char = decrypt_index(i, ct[i], wheels_data)
        plaintext.append(p_char)
        if p_char == '?':
            undetermined_count += 1
            undetermined_indices.append(i)
    
    # Write output
    pt_str = ''.join(plaintext)
    with open(args.out, 'w') as f:
        f.write(pt_str)
    
    print(f"Derived plaintext written to {args.out}")
    print(f"Undetermined positions: {undetermined_count}/{len(ct)}")
    if undetermined_count > 0 and undetermined_count <= 20:
        print(f"Undetermined indices: {undetermined_indices[:20]}")
    
    # Show the BERLIN/CLOCK corridor
    print(f"\nIndices 63-73 (BERLIN/CLOCK corridor):")
    print(f"  Ciphertext: {ct[63:74]}")
    print(f"  Derived:    {pt_str[63:74]}")

if __name__ == "__main__":
    main()