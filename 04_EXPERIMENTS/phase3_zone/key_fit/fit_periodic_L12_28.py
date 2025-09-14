#!/usr/bin/env python3
"""
Fit longer periodic keys (L=12-28) to anchor constraints
Plan H: Testing modest periods with special focus on 24 (Urania) and 28 (lattice)
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import itertools

# Add necessary paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / '03_SOLVERS' / 'zone_mask_v1' / 'scripts'))
from cipher_families import VigenereCipher, BeaufortCipher

# Import route utilities
sys.path.insert(0, str(Path(__file__).parent))
try:
    from route_utils import apply_route, apply_route_inverse
except ImportError:
    # Routes not available, use identity only
    def apply_route(text, route_type, **params):
        return text
    def apply_route_inverse(text, route_type, **params):
        return text


def load_ciphertext() -> str:
    """Load K4 ciphertext"""
    ct_path = Path(__file__).parent.parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
    with open(ct_path, 'r') as f:
        return f.read().strip().upper()


def derive_key_from_anchors(ciphertext: str, route_type: str = 'identity', 
                           family: str = 'vigenere', tableau: str = 'kryptos') -> List[Dict]:
    """
    Derive required key letters at anchor positions after route
    
    Returns:
        List of constraints {idx, c, p, k} where k is required key letter
    """
    # Apply route to ciphertext
    if route_type == 'ring24':
        routed_ct = apply_route(ciphertext, 'ring24', rows=24, cols=4, passes=1)
    elif route_type == 'serpentine':
        routed_ct = apply_route(ciphertext, 'serpentine', rows=7, cols=14, passes=1)
    else:
        routed_ct = ciphertext
    
    # Define anchors
    anchors = [
        ('EAST', 21, 24),
        ('NORTHEAST', 25, 33),
        ('BERLIN', 63, 68),
        ('CLOCK', 69, 73)
    ]
    
    constraints = []
    
    # Build KRYPTOS tableau
    if tableau == 'kryptos':
        keyword = 'KRYPTOS'
        keyed_alphabet = []
        used = set()
        for char in keyword:
            if char not in used:
                keyed_alphabet.append(char)
                used.add(char)
        for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if char not in used:
                keyed_alphabet.append(char)
        alphabet = ''.join(keyed_alphabet)
    else:
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    for anchor_text, start, end in anchors:
        for i, pt_char in enumerate(anchor_text):
            idx = start + i
            if idx < len(routed_ct):
                ct_char = routed_ct[idx]
                
                # Calculate required key letter
                ct_pos = alphabet.index(ct_char)
                pt_pos = alphabet.index(pt_char)
                
                if family == 'vigenere':
                    # k = c - p mod 26
                    key_pos = (ct_pos - pt_pos) % 26
                else:  # beaufort
                    # k = c + p mod 26
                    key_pos = (ct_pos + pt_pos) % 26
                
                key_char = alphabet[key_pos]
                
                constraints.append({
                    'idx': idx,
                    'c': ct_char,
                    'p': pt_char,
                    'k': key_char
                })
    
    return constraints


def fit_periodic_key(constraints: List[Dict], L: int, phase: int = 0,
                     control_resets: List[int] = None) -> Optional[str]:
    """
    Try to fit a periodic key of length L with given phase
    
    Args:
        constraints: List of {idx, k} requirements
        L: Period length
        phase: Initial phase offset
        control_resets: Positions where phase resets occur
        
    Returns:
        Key string if consistent, None otherwise
    """
    key = ['?'] * L
    
    for constraint in constraints:
        idx = constraint['idx']
        required = constraint['k']
        
        # Handle phase resets
        current_phase = phase
        if control_resets:
            for reset_pos in control_resets:
                if idx >= reset_pos:
                    current_phase = 0  # Reset phase at control positions
        
        # Calculate position in key
        key_pos = (idx - current_phase) % L
        
        if key[key_pos] == '?':
            key[key_pos] = required
        elif key[key_pos] != required:
            return None  # Inconsistency
    
    # If any positions unfilled, use 'A' as default
    for i in range(L):
        if key[i] == '?':
            key[i] = 'A'
    
    return ''.join(key)


def test_full_decryption(key: str, phase: int, route_type: str, family: str,
                         control_resets: List[int] = None) -> Optional[str]:
    """Test full decryption and return plaintext"""
    ciphertext = load_ciphertext()
    
    # Apply route
    if route_type == 'ring24':
        routed_ct = apply_route(ciphertext, 'ring24', rows=24, cols=4, passes=1)
    elif route_type == 'serpentine':
        routed_ct = apply_route(ciphertext, 'serpentine', rows=7, cols=14, passes=1)
    else:
        routed_ct = ciphertext
    
    # Build full keystream
    keystream = []
    L = len(key)
    current_phase = phase
    
    for i in range(len(routed_ct)):
        if control_resets and i in control_resets:
            current_phase = 0
        keystream.append(key[(i - current_phase) % L])
    
    full_key = ''.join(keystream)
    
    # Decrypt
    if family == 'vigenere':
        cipher = VigenereCipher(tableau='kryptos')
        plaintext = cipher.decrypt(routed_ct, full_key)
    else:
        cipher = BeaufortCipher(tableau='kryptos')
        plaintext = cipher.decrypt(routed_ct, full_key)
    
    # Apply inverse route
    if route_type == 'ring24':
        plaintext = apply_route_inverse(plaintext, 'ring24', rows=24, cols=4, passes=1)
    elif route_type == 'serpentine':
        plaintext = apply_route_inverse(plaintext, 'serpentine', rows=7, cols=14, passes=1)
    
    return plaintext


def verify_anchors(plaintext: str) -> int:
    """Count matching anchors"""
    anchors = [
        ('EAST', 21, 24),
        ('NORTHEAST', 25, 33),
        ('BERLIN', 63, 68),
        ('CLOCK', 69, 73)
    ]
    
    matches = 0
    for anchor_text, start, end in anchors:
        if plaintext[start:end+1] == anchor_text:
            matches += 1
    
    return matches


def find_longer_period_fits() -> List[Dict]:
    """Find periodic keys with L=12-28"""
    
    results = []
    ciphertext = load_ciphertext()
    
    # Test parameters
    periods = list(range(12, 29))  # 12 to 28
    families = ['vigenere', 'beaufort']
    routes = ['identity', 'ring24', 'serpentine']
    control_options = [None, [63, 69]]  # No control or resets at 63, 69
    
    print("=" * 70)
    print("LONGER PERIOD KEY FITTING (L=12-28)")
    print("=" * 70)
    
    special_periods = [24, 28]  # Focus on these
    
    for L in periods:
        is_special = L in special_periods
        if is_special:
            print(f"\n{'*' * 40}")
            print(f"TESTING SPECIAL PERIOD L={L}")
            print(f"{'*' * 40}")
        else:
            print(f"\nTesting period L={L}")
        
        for family in families:
            for route in routes:
                # Derive constraints from anchors
                constraints = derive_key_from_anchors(ciphertext, route, family, 'kryptos')
                
                for control_resets in control_options:
                    control_name = "static" if control_resets is None else f"resets@{control_resets}"
                    
                    # Try all phases
                    for phase in range(L):
                        # Try to fit key
                        key = fit_periodic_key(constraints, L, phase, control_resets)
                        
                        if key:
                            # Test full decryption
                            plaintext = test_full_decryption(key, phase, route, family, control_resets)
                            
                            if plaintext:
                                matches = verify_anchors(plaintext)
                                
                                if matches > 0:
                                    result = {
                                        'period': L,
                                        'family': family,
                                        'route': route,
                                        'phase': phase,
                                        'control': control_name,
                                        'key': key,
                                        'matches': matches,
                                        'plaintext_sample': plaintext[:40],
                                        'description': f"L={L} {family} {route} φ={phase} {control_name}"
                                    }
                                    results.append(result)
                                    
                                    if matches == 4:
                                        print(f"  ✓✓✓ FULL MATCH: {result['description']}")
                                        print(f"      Key: {key}")
                                        print(f"      Sample: {plaintext[:40]}")
                                    elif is_special:
                                        print(f"  ✓ Partial ({matches}/4): {result['description']}")
    
    print(f"\nTotal configurations with matches: {len(results)}")
    return results


def main():
    """Find longer period configurations"""
    
    results = find_longer_period_fits()
    
    # Save results
    output_path = Path(__file__).parent / 'periodic_L12_28_fits.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if results:
        # Sort by matches
        results.sort(key=lambda x: x['matches'], reverse=True)
        
        # Check for full matches
        full_matches = [r for r in results if r['matches'] == 4]
        
        if full_matches:
            print("\n" + "!" * 70)
            print("SOLUTION CANDIDATE FOUND!")
            print("!" * 70)
            
            for match in full_matches[:3]:  # Show top 3
                print(f"\n{match['description']}")
                print(f"Period: {match['period']}, Key: {match['key']}")
                print(f"Plaintext sample: {match['plaintext_sample']}")
                
                # Create manifest path
                manifest_name = f"L{match['period']}_{match['route']}_{match['family']}_{match['control']}.json"
                print(f"Suggested manifest: {manifest_name}")
        else:
            print(f"\nPartial matches found: {len(results)}")
            for r in results[:5]:
                print(f"  - {r['description']}: {r['matches']}/4 anchors")
    else:
        print("\nNo configurations found with L=12-28.")
        print("This falsifies modest-period polyalphabetic keys.")
        print("\nNext: Plan I - Minimal masks with classical ciphers")
    
    print(f"\nResults saved to: {output_path}")


if __name__ == '__main__':
    main()