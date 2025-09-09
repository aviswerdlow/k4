#!/usr/bin/env python3
"""
Minimal K4 plaintext re-deriver using pure Python stdlib.
No external dependencies, no repo imports.
Demonstrates the mathematical derivation from CT + proof → PT.
"""

import json
import argparse
from typing import Dict, List, Tuple

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
    """Decrypt a single index using the appropriate wheel"""
    # Get class
    cls = class_function(i)
    wheel = wheels[cls]
    
    # Get wheel parameters
    family = wheel['family']
    period = wheel['L']
    phase = wheel['phase']
    residues = wheel['residues']
    
    # Calculate slot
    slot = get_wheel_slot(i, phase, period)
    
    # Get key residue at this slot
    k = residues[slot]
    
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
        print(f"  Key residue (K): {k}")
        print(f"  Ciphertext (C): {ct_char} = {c}")
        if family == 'vigenere':
            print(f"  Decrypt: P = C - K = {c} - {k} = {p} (mod 26)")
        elif family == 'beaufort':
            print(f"  Decrypt: P = K - C = {k} - {c} = {p} (mod 26)")
        else:  # variant_beaufort
            print(f"  Decrypt: P = C + K = {c} + {k} = {p} (mod 26)")
        print(f"  Plaintext: {num_to_letter(p)}")
    
    return num_to_letter(p)

def parse_proof(proof_path: str) -> Dict:
    """Parse the proof JSON and extract wheel configurations"""
    with open(proof_path, 'r') as f:
        proof = json.load(f)
    
    wheels = {}
    if 'per_class' in proof:
        for class_data in proof['per_class']:
            cls = class_data['class_id']
            wheels[cls] = {
                'family': class_data['family'],
                'L': class_data['L'],
                'phase': class_data['phase'],
                'residues': class_data['residues']
            }
    
    return wheels

def main():
    parser = argparse.ArgumentParser(description='Minimal K4 re-deriver (pure Python)')
    parser.add_argument('--ct', required=True, help='Path to ciphertext file')
    parser.add_argument('--proof', required=True, help='Path to proof JSON')
    parser.add_argument('--out', help='Output path for plaintext')
    parser.add_argument('--explain', type=int, help='Explain derivation at index i')
    
    args = parser.parse_args()
    
    # Read ciphertext
    with open(args.ct, 'r') as f:
        ct = f.read().strip().upper()
    
    # Parse proof to get wheels
    wheels = parse_proof(args.proof)
    
    # If explain mode, just explain that index
    if args.explain is not None:
        i = args.explain
        if 0 <= i < len(ct):
            decrypt_index(i, ct[i], wheels, explain=True)
        else:
            print(f"Index {i} out of range (0-{len(ct)-1})")
        return
    
    # Regular derivation mode requires --out
    if not args.out:
        print("Error: --out is required for derivation mode")
        return
    
    # Decrypt all 97 letters
    plaintext = []
    for i in range(len(ct)):
        plaintext.append(decrypt_index(i, ct[i], wheels))
    
    # Write output
    pt_str = ''.join(plaintext)
    with open(args.out, 'w') as f:
        f.write(pt_str)
    
    print(f"Derived plaintext written to {args.out}")
    print(f"SHA-256 verification:")
    print(f"  Run: shasum -a 256 {args.out}")
    print(f"  Expected: 4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79")

if __name__ == '__main__':
    main()