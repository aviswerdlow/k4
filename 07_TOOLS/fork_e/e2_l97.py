#!/usr/bin/env python3
"""
E2 - L=97 Single Track (Sanity/Falsification Test)
Test if using L=97 (prime period) could work
"""

import json
import os
import hashlib
from typing import Dict, List, Optional

MASTER_SEED = 1337

def compute_class_baseline(i):
    """Baseline class function"""
    return ((i % 2) * 3) + (i % 3)

def load_data():
    """Load all required data"""
    with open('../../02_DATA/ciphertext_97.txt', 'r') as f:
        ciphertext = f.read().strip()
    
    with open('../../01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt', 'r') as f:
        canonical_pt = f.read().strip()
    
    anchors = []
    for start, end in [(21, 24), (25, 33), (63, 68), (69, 73)]:
        for i in range(start, end + 1):
            anchors.append(i)
    
    tail = list(range(74, 97))
    
    return ciphertext, canonical_pt, anchors, tail

def test_l97_single_track(ciphertext, canonical_pt, anchors, tail):
    """Test L=97 with single track (each position unique)"""
    L = 97
    
    # With L=97, each position is its own unique slot
    # Try to fit a single wheel
    wheel = [None] * L
    
    # Determine key values from known positions
    known_positions = set(anchors) | set(tail)
    
    for pos in known_positions:
        c_char = ciphertext[pos]
        p_char = canonical_pt[pos]
        
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        # Try Vigenere-style
        k_val = (c_val - p_val) % 26
        
        if wheel[pos] is None:
            wheel[pos] = k_val
        elif wheel[pos] != k_val:
            # Conflict - L=97 single track doesn't work
            return None, f"Conflict at position {pos}"
    
    # Apply to unknown positions
    derived = []
    unknowns = 0
    
    for i in range(97):
        if i in known_positions:
            derived.append(canonical_pt[i])
        elif wheel[i] is not None:
            c_char = ciphertext[i]
            c_val = ord(c_char) - ord('A')
            p_val = (c_val - wheel[i]) % 26
            derived.append(chr(p_val + ord('A')))
        else:
            derived.append('?')
            unknowns += 1
    
    return ''.join(derived), unknowns

def test_l97_multitrack(ciphertext, canonical_pt, anchors, tail):
    """Test L=97 with multiple tracks based on class"""
    L = 97
    
    # Create 6 wheels of length 97
    wheels = {}
    for c in range(6):
        wheels[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'residues': [None] * L
        }
    
    known_positions = set(anchors) | set(tail)
    
    # Fill from known positions
    for pos in known_positions:
        c = compute_class_baseline(pos)
        s = pos  # With L=97, slot = position
        
        c_char = ciphertext[pos]
        p_char = canonical_pt[pos]
        
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        if wheels[c]['family'] == 'vigenere':
            k_val = (c_val - p_val) % 26
        else:
            k_val = (p_val + c_val) % 26
        
        if wheels[c]['residues'][s] is None:
            wheels[c]['residues'][s] = k_val
        elif wheels[c]['residues'][s] != k_val:
            return None, f"Conflict at position {pos} in class {c}"
    
    # Apply to unknown positions
    derived = []
    unknowns = 0
    
    for i in range(97):
        if i in known_positions:
            derived.append(canonical_pt[i])
        else:
            c = compute_class_baseline(i)
            if wheels[c]['residues'][i] is not None:
                c_char = ciphertext[i]
                c_val = ord(c_char) - ord('A')
                k_val = wheels[c]['residues'][i]
                
                if wheels[c]['family'] == 'vigenere':
                    p_val = (c_val - k_val) % 26
                else:
                    p_val = (k_val - c_val) % 26
                
                derived.append(chr(p_val + ord('A')))
            else:
                derived.append('?')
                unknowns += 1
    
    return ''.join(derived), unknowns

def verify_constraints(plaintext, canonical_pt, anchors, tail):
    """Verify anchors and tail are preserved"""
    for i in anchors + tail:
        if plaintext[i] != canonical_pt[i]:
            return False
    return True

def main():
    """Run E2 L=97 tests"""
    print("=== E2: L=97 Single Track Test ===\n")
    
    os.makedirs('E2_L97', exist_ok=True)
    
    # Load data
    ciphertext, canonical_pt, anchors, tail = load_data()
    
    print("Testing L=97 as sanity check...")
    print(f"Known positions: {len(anchors) + len(tail)}")
    
    # Test 1: Single track L=97
    print("\n1. Single track (one wheel, L=97)...")
    result1 = test_l97_single_track(ciphertext, canonical_pt, anchors, tail)
    
    if result1[0] is None:
        print(f"   Failed: {result1[1]}")
    else:
        pt1, unk1 = result1
        valid1 = verify_constraints(pt1, canonical_pt, anchors, tail)
        print(f"   Unknowns: {unk1}")
        print(f"   Valid: {valid1}")
        
        if unk1 == 50:
            print("   Result: No improvement over L=17 (still 50 unknowns)")
    
    # Test 2: Multi-track L=97
    print("\n2. Multi-track (6 wheels, L=97)...")
    result2 = test_l97_multitrack(ciphertext, canonical_pt, anchors, tail)
    
    if result2[0] is None:
        print(f"   Failed: {result2[1]}")
    else:
        pt2, unk2 = result2
        valid2 = verify_constraints(pt2, canonical_pt, anchors, tail)
        print(f"   Unknowns: {unk2}")
        print(f"   Valid: {valid2}")
        
        if unk2 == 50:
            print("   Result: No improvement over L=17 (still 50 unknowns)")
    
    # Summary
    print("\n=== Summary ===")
    print("L=97 provides no advantage over L=17")
    print("With 97 positions and 47 constraints, we still have 50 unknowns")
    print("This confirms the mathematical necessity of the constraint count")
    
    # Save results
    results = {
        'test': 'L=97',
        'single_track': 'Failed - conflicts' if result1[0] is None else f"{unk1} unknowns",
        'multi_track': 'Failed - conflicts' if result2[0] is None else f"{unk2} unknowns",
        'conclusion': 'L=97 offers no improvement over L=17'
    }
    
    with open('E2_L97/RESULT.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to E2_L97/")

if __name__ == "__main__":
    main()