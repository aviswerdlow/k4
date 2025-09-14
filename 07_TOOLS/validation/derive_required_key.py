#!/usr/bin/env python3
"""
Derive required key substring for specific plaintext at specific position
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict

# Add cipher_families to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / '03_SOLVERS' / 'zone_mask_v1' / 'scripts'))
from cipher_families import VigenereCipher, BeaufortCipher


def derive_key_for_window(ciphertext: str, plaintext: str, start_idx: int, 
                          family: str = 'vigenere', tableau: str = 'kryptos') -> str:
    """
    Derive the key required to decrypt a ciphertext window to plaintext
    
    Args:
        ciphertext: Full ciphertext
        plaintext: Desired plaintext for window
        start_idx: Starting index in ciphertext (0-based)
        family: 'vigenere' or 'beaufort'
        tableau: 'standard' or 'kryptos'
    
    Returns:
        Required key substring
    """
    # Extract ciphertext window
    ct_window = ciphertext[start_idx:start_idx + len(plaintext)]
    
    if len(ct_window) != len(plaintext):
        raise ValueError(f"Ciphertext window too short at position {start_idx}")
    
    # Create cipher
    if family == 'vigenere':
        cipher = VigenereCipher(tableau=tableau)
    elif family == 'beaufort':
        cipher = BeaufortCipher(tableau=tableau)
    else:
        raise ValueError(f"Unknown cipher family: {family}")
    
    # Derive key character by character
    key = []
    for i in range(len(plaintext)):
        ct_char = ct_window[i]
        pt_char = plaintext[i]
        
        # Try all possible key characters
        for test_key in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if cipher.decrypt(ct_char, test_key) == pt_char:
                key.append(test_key)
                break
        else:
            # No key character found
            key.append('?')
    
    return ''.join(key)


def derive_all_anchors(ciphertext_path: Path = None) -> Dict:
    """Derive required keys for all four anchors"""
    
    # Load ciphertext
    if ciphertext_path is None:
        ciphertext_path = Path(__file__).parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
    
    with open(ciphertext_path, 'r') as f:
        ciphertext = f.read().strip().upper()
    
    # Define anchors
    anchors = {
        'EAST': (21, 24),
        'NORTHEAST': (25, 33),
        'BERLIN': (63, 68),
        'CLOCK': (69, 73)
    }
    
    results = {
        'anchors': {},
        'ciphertext_windows': {},
        'required_keys': {
            'vigenere': {'standard': {}, 'kryptos': {}},
            'beaufort': {'standard': {}, 'kryptos': {}}
        }
    }
    
    for anchor_name, (start, end) in anchors.items():
        # Store anchor info
        results['anchors'][anchor_name] = {
            'text': anchor_name,
            'start': start,
            'end': end,
            'length': end - start + 1
        }
        
        # Extract ciphertext window
        ct_window = ciphertext[start:end+1]
        results['ciphertext_windows'][anchor_name] = ct_window
        
        # Derive keys for each cipher/tableau combination
        for family in ['vigenere', 'beaufort']:
            for tableau in ['standard', 'kryptos']:
                key = derive_key_for_window(ciphertext, anchor_name, start, family, tableau)
                results['required_keys'][family][tableau][anchor_name] = {
                    'key': key,
                    'position': f"{start}-{end}",
                    'validates': '?' not in key
                }
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Derive required key for anchor')
    parser.add_argument('--ct_window_idx', type=int, 
                       help='Starting index of window in ciphertext (0-based)')
    parser.add_argument('--pt', type=str,
                       help='Desired plaintext for window')
    parser.add_argument('--family', type=str, default='vigenere',
                       choices=['vigenere', 'beaufort'],
                       help='Cipher family')
    parser.add_argument('--tableau', type=str, default='kryptos',
                       choices=['standard', 'kryptos'],
                       help='Tableau type')
    parser.add_argument('--all_anchors', action='store_true',
                       help='Derive keys for all four anchors')
    parser.add_argument('--output', type=str,
                       help='Output JSON file for results')
    
    args = parser.parse_args()
    
    if args.all_anchors:
        # Derive for all anchors
        results = derive_all_anchors()
        
        # Print summary
        print("=" * 70)
        print("REQUIRED KEYS FOR ALL ANCHORS")
        print("=" * 70)
        
        for family in ['vigenere', 'beaufort']:
            for tableau in ['kryptos', 'standard']:
                print(f"\n{family.upper()} with {tableau.upper()} tableau:")
                print("-" * 40)
                
                for anchor in ['EAST', 'NORTHEAST', 'BERLIN', 'CLOCK']:
                    key_info = results['required_keys'][family][tableau][anchor]
                    ct_window = results['ciphertext_windows'][anchor]
                    print(f"  {anchor:10} [{key_info['position']:7}]: {ct_window:10} → {key_info['key']}")
        
        # Save if requested
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to: {output_path}")
    
    else:
        # Single window derivation
        # Load ciphertext
        ct_path = Path(__file__).parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
        with open(ct_path, 'r') as f:
            ciphertext = f.read().strip().upper()
        
        # Derive key
        key = derive_key_for_window(ciphertext, args.pt.upper(), args.ct_window_idx,
                                   args.family, args.tableau)
        
        # Extract ciphertext window
        ct_window = ciphertext[args.ct_window_idx:args.ct_window_idx + len(args.pt)]
        
        # Print result
        print(f"Cipher: {args.family} with {args.tableau} tableau")
        print(f"Position: {args.ct_window_idx}-{args.ct_window_idx + len(args.pt) - 1}")
        print(f"Ciphertext: {ct_window}")
        print(f"Plaintext:  {args.pt.upper()}")
        print(f"Required key: {key}")
        
        if '?' in key:
            print("WARNING: Could not derive complete key (contains '?')")


if __name__ == '__main__':
    main()