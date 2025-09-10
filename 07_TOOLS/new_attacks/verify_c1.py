#!/usr/bin/env python3
"""
Verify C1 L=7 claim with strict validation
"""

import json
import os

MASTER_SEED = 1337

def compute_class_baseline(i):
    """Baseline class function: ((i%2)*3)+(i%3)"""
    return ((i % 2) * 3) + (i % 3)

def load_data():
    """Load all required data"""
    # Load ciphertext
    with open('../../02_DATA/ciphertext_97.txt', 'r') as f:
        ciphertext = f.read().strip()
    
    # Load canonical plaintext
    with open('../../01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt', 'r') as f:
        canonical_pt = f.read().strip()
    
    # Define anchors
    anchors = []
    for start, end in [(21, 24), (25, 33), (63, 68), (69, 73)]:
        for i in range(start, end + 1):
            anchors.append(i)
    
    # Define tail
    tail = list(range(74, 97))
    
    # Define baseline unknowns (everything except anchors+tail)
    all_constrained = set(anchors) | set(tail)
    baseline_unknowns = [i for i in range(97) if i not in all_constrained]
    
    return ciphertext, canonical_pt, anchors, tail, baseline_unknowns

def build_l17_baseline(ciphertext, canonical_pt, anchors, tail):
    """Build L=17 baseline wheels from anchors+tail"""
    L = 17
    wheels = {}
    
    # Initialize wheels
    for c in range(6):
        wheels[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L,
            'residues': [None] * L
        }
    
    # Apply constraints
    all_constraints = set(anchors) | set(tail)
    
    for pos in all_constraints:
        c = compute_class_baseline(pos)
        s = pos % L
        
        c_char = ciphertext[pos]
        p_char = canonical_pt[pos]
        
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        if wheels[c]['family'] == 'vigenere':
            k_val = (c_val - p_val) % 26
        else:
            k_val = (p_val + c_val) % 26
        
        wheels[c]['residues'][s] = k_val
    
    return wheels

def derive_plaintext_l17(ciphertext, wheels):
    """Derive plaintext with L=17"""
    L = 17
    derived = []
    unknown_indices = []
    
    for i in range(97):
        c = compute_class_baseline(i)
        s = i % L
        
        if wheels[c]['residues'][s] is not None:
            c_char = ciphertext[i]
            c_val = ord(c_char) - ord('A')
            k_val = wheels[c]['residues'][s]
            
            if wheels[c]['family'] == 'vigenere':
                p_val = (c_val - k_val) % 26
            else:
                p_val = (k_val - c_val) % 26
            
            derived.append(chr(p_val + ord('A')))
        else:
            derived.append('?')
            unknown_indices.append(i)
    
    return ''.join(derived), unknown_indices

def test_l7_overlay(ciphertext, canonical_pt, anchors, tail):
    """Test L=7 overlay on head"""
    L = 7
    wheels = {}
    
    # Initialize L=7 wheels
    for c in range(6):
        wheels[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L,
            'residues': [None] * L
        }
    
    # Apply constraints from anchors and tail
    all_constraints = set(anchors) | set(tail)
    
    for pos in all_constraints:
        c = compute_class_baseline(pos)
        s = pos % L  # Now using mod 7
        
        c_char = ciphertext[pos]
        p_char = canonical_pt[pos]
        
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        if wheels[c]['family'] == 'vigenere':
            k_val = (c_val - p_val) % 26
        else:
            k_val = (p_val + c_val) % 26
        
        # Check for conflicts
        if wheels[c]['residues'][s] is not None:
            if wheels[c]['residues'][s] != k_val:
                print(f"  Conflict at pos {pos}: slot {s} has {wheels[c]['residues'][s]}, want {k_val}")
        else:
            wheels[c]['residues'][s] = k_val
    
    # Derive plaintext with L=7
    derived = []
    unknown_indices = []
    
    for i in range(97):
        c = compute_class_baseline(i)
        s = i % L
        
        if wheels[c]['residues'][s] is not None:
            c_char = ciphertext[i]
            c_val = ord(c_char) - ord('A')
            k_val = wheels[c]['residues'][s]
            
            if wheels[c]['family'] == 'vigenere':
                p_val = (c_val - k_val) % 26
            else:
                p_val = (k_val - c_val) % 26
            
            derived.append(chr(p_val + ord('A')))
        else:
            derived.append('?')
            unknown_indices.append(i)
    
    return ''.join(derived), unknown_indices

def verify_constraints(plaintext, canonical_pt, anchors, tail):
    """Verify anchors and tail are preserved"""
    errors = []
    
    # Check anchors
    anchor_ranges = [(21, 24, 'EAST'), (25, 33, 'NORTHEAST'), (63, 68, 'BERLIN'), (69, 73, 'CLOCK')]
    for start, end, name in anchor_ranges:
        for i in range(start, end + 1):
            if plaintext[i] != canonical_pt[i]:
                errors.append(f"Anchor {name} position {i}: got '{plaintext[i]}', want '{canonical_pt[i]}'")
    
    # Check tail
    for i in range(74, 97):
        if plaintext[i] != canonical_pt[i]:
            errors.append(f"Tail position {i}: got '{plaintext[i]}', want '{canonical_pt[i]}'")
    
    return errors

def main():
    """Run verification"""
    print("=== C1 L=7 Verification ===\n")
    
    # Load data
    ciphertext, canonical_pt, anchors, tail, baseline_unknowns = load_data()
    
    print(f"Baseline unknowns: {len(baseline_unknowns)}")
    print(f"Anchors: {len(anchors)} positions")
    print(f"Tail: {len(tail)} positions")
    print(f"Total constrained: {len(anchors) + len(tail)}")
    
    # Test L=17 baseline
    print("\n1. L=17 Baseline:")
    wheels_17 = build_l17_baseline(ciphertext, canonical_pt, anchors, tail)
    pt_17, unknown_17 = derive_plaintext_l17(ciphertext, wheels_17)
    print(f"   Unknown positions: {len(unknown_17)}")
    
    errors_17 = verify_constraints(pt_17, canonical_pt, anchors, tail)
    if errors_17:
        print(f"   ERRORS: {len(errors_17)} constraint violations")
        for e in errors_17[:3]:
            print(f"     - {e}")
    else:
        print("   ✓ All constraints preserved")
    
    # Test L=7 overlay
    print("\n2. L=7 Overlay Test:")
    pt_7, unknown_7 = test_l7_overlay(ciphertext, canonical_pt, anchors, tail)
    print(f"   Unknown positions: {len(unknown_7)}")
    
    errors_7 = verify_constraints(pt_7, canonical_pt, anchors, tail)
    if errors_7:
        print(f"   ERRORS: {len(errors_7)} constraint violations")
        for e in errors_7[:3]:
            print(f"     - {e}")
    else:
        print("   ✓ All constraints preserved")
    
    # Compare
    print("\n3. Comparison:")
    print(f"   L=17: {len(unknown_17)} unknowns")
    print(f"   L=7:  {len(unknown_7)} unknowns")
    print(f"   Reduction: {len(unknown_17) - len(unknown_7)}")
    
    if len(unknown_7) < len(unknown_17):
        print(f"\n   SUCCESS: Reduced unknowns from {len(unknown_17)} to {len(unknown_7)}")
        
        # Show which positions were resolved
        resolved = set(unknown_17) - set(unknown_7)
        if resolved:
            print(f"   Resolved positions: {sorted(resolved)[:10]}...")
    else:
        print("\n   NO REDUCTION")
    
    # Save results
    results = {
        'l17_unknowns': len(unknown_17),
        'l7_unknowns': len(unknown_7),
        'reduction': len(unknown_17) - len(unknown_7),
        'constraints_preserved': len(errors_7) == 0,
        'plaintext_l7': pt_7,
        'unknown_indices_l7': unknown_7
    }
    
    os.makedirs('C1_verification', exist_ok=True)
    with open('C1_verification/results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    with open('C1_verification/PT_PARTIAL.txt', 'w') as f:
        f.write(pt_7)
    
    print("\nResults saved to C1_verification/")

if __name__ == "__main__":
    main()