#!/usr/bin/env python3
"""
Phase 1 & 2: Test L=15 with anchors only, then with tail.
Pure algebra, no semantics.
"""

import json
import csv
from collections import defaultdict
import os

def compute_class_baseline(i):
    """Baseline class function: ((i%2)*3)+(i%3)"""
    return ((i % 2) * 3) + (i % 3)

def load_ciphertext():
    """Load the 97-character ciphertext"""
    with open('../../02_DATA/ciphertext_97.txt', 'r') as f:
        return f.read().strip()

def load_anchors():
    """Load anchor positions and plaintext"""
    return {
        'EAST': (21, 24),
        'NORTHEAST': (25, 33),
        'BERLIN': (63, 68),
        'CLOCK': (69, 73)
    }

def get_tail_plaintext():
    """Get tail plaintext from published solution (indices 74-96)"""
    # Reading from winner file
    with open('../../01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt', 'r') as f:
        full_pt = f.read().strip()
    # Note: File uses 1-indexed, we use 0-indexed
    return full_pt[74:97]  # Positions 74-96 (0-indexed)

def test_mechanism_L15(ciphertext, anchors, phase=0, enforce_option_a=True):
    """
    Test L=15 mechanism with given anchors.
    Returns wheels and stats.
    """
    L = 15
    
    # Initialize wheels for 6 classes
    wheels = {}
    for c in range(6):
        wheels[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L,
            'phase': phase,
            'residues': [None] * L
        }
    
    # Process anchors to force residues
    forced_count = 0
    conflicts = []
    
    for crib_text, (start, end) in anchors.items():
        for i, p_char in enumerate(crib_text):
            pos = start + i
            if pos > end:
                break
                
            c = compute_class_baseline(pos)
            s = (pos + phase) % L
            
            c_char = ciphertext[pos]
            c_val = ord(c_char) - ord('A')
            p_val = ord(p_char) - ord('A')
            
            # Compute residue based on family
            if wheels[c]['family'] == 'vigenere':
                k_val = (c_val - p_val) % 26
            else:  # beaufort
                k_val = (p_val + c_val) % 26
            
            # Option-A check for Beaufort
            if enforce_option_a and wheels[c]['family'] == 'beaufort' and k_val == 0:
                conflicts.append(f"Option-A violation at pos {pos}")
                continue
            
            # Check for conflicts
            if wheels[c]['residues'][s] is not None:
                if wheels[c]['residues'][s] != k_val:
                    conflicts.append(f"Conflict at class {c}, slot {s}: {wheels[c]['residues'][s]} vs {k_val}")
            else:
                wheels[c]['residues'][s] = k_val
                forced_count += 1
    
    return wheels, forced_count, conflicts

def derive_plaintext(ciphertext, wheels, L=15, phase=0):
    """
    Derive plaintext using wheels.
    Returns plaintext string with '?' for unknowns.
    """
    plaintext = []
    derived_count = 0
    
    for i in range(len(ciphertext)):
        c = compute_class_baseline(i)
        s = (i + phase) % L
        
        if wheels[c]['residues'][s] is not None:
            c_char = ciphertext[i]
            c_val = ord(c_char) - ord('A')
            k_val = wheels[c]['residues'][s]
            
            if wheels[c]['family'] == 'vigenere':
                p_val = (c_val - k_val) % 26
            else:  # beaufort
                p_val = (k_val - c_val) % 26
            
            plaintext.append(chr(p_val + ord('A')))
            derived_count += 1
        else:
            plaintext.append('?')
    
    return ''.join(plaintext), derived_count

def compute_slot_hitmap(L=15):
    """
    Compute which indices hit which slots for each class.
    """
    hitmap = defaultdict(lambda: defaultdict(list))
    
    for i in range(97):
        c = compute_class_baseline(i)
        s = i % L
        hitmap[c][s].append(i)
    
    return hitmap

def phase1_anchors_only():
    """Phase 1: Test L=15 with anchors only"""
    print("\n=== PHASE 1: L=15 with Anchors Only ===")
    
    ciphertext = load_ciphertext()
    anchors = load_anchors()
    
    # Test with phase=0
    wheels, forced_slots, conflicts = test_mechanism_L15(ciphertext, anchors, phase=0)
    
    if conflicts:
        print(f"Conflicts found: {conflicts}")
    
    # Derive plaintext
    plaintext, derived_count = derive_plaintext(ciphertext, wheels, L=15)
    unknown_count = 97 - derived_count
    
    print(f"\nResults:")
    print(f"  Forced slots: {forced_slots}")
    print(f"  Derived positions: {derived_count}")
    print(f"  Unknown positions: {unknown_count}")
    
    # Create output directory
    os.makedirs('L15/anchors_only', exist_ok=True)
    
    # Save plaintext
    with open('L15/anchors_only/PT_PARTIAL.txt', 'w') as f:
        f.write(plaintext)
    
    # Save wheels
    wheels_json = {}
    for c, w in wheels.items():
        wheels_json[str(c)] = {
            'family': w['family'],
            'L': w['L'],
            'phase': w['phase'],
            'residues': w['residues']
        }
    
    with open('L15/anchors_only/WHEELS.json', 'w') as f:
        json.dump(wheels_json, f, indent=2)
    
    # Save counts
    with open('L15/anchors_only/COUNTS.json', 'w') as f:
        json.dump({
            'derived_count': derived_count,
            'unknown_count': unknown_count,
            'forced_slots': forced_slots
        }, f, indent=2)
    
    # Save slot hitmap
    hitmap = compute_slot_hitmap(L=15)
    with open('L15/anchors_only/SLOT_HITMAP.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Class', 'Slot', 'Indices', 'Count'])
        for c in range(6):
            for s in range(15):
                indices = hitmap[c][s]
                writer.writerow([c, s, ' '.join(map(str, indices)), len(indices)])
    
    return wheels, derived_count, unknown_count

def phase2_add_tail(wheels):
    """Phase 2: Add tail as coverage test"""
    print("\n=== PHASE 2: L=15 with Anchors + Tail ===")
    
    ciphertext = load_ciphertext()
    tail_plaintext = get_tail_plaintext()
    
    print(f"Tail plaintext (74-96): {tail_plaintext}")
    
    # Force residues from tail
    L = 15
    phase = 0
    tail_forced = 0
    
    for i, p_char in enumerate(tail_plaintext):
        pos = 74 + i  # Tail starts at position 74
        c = compute_class_baseline(pos)
        s = (pos + phase) % L
        
        # Skip if already forced
        if wheels[c]['residues'][s] is not None:
            continue
        
        c_char = ciphertext[pos]
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        # Compute residue
        if wheels[c]['family'] == 'vigenere':
            k_val = (c_val - p_val) % 26
        else:  # beaufort
            k_val = (p_val + c_val) % 26
        
        wheels[c]['residues'][s] = k_val
        tail_forced += 1
    
    # Derive with augmented wheels
    plaintext, derived_count = derive_plaintext(ciphertext, wheels, L=15)
    unknown_count = 97 - derived_count
    
    print(f"\nResults:")
    print(f"  Tail forced: {tail_forced} additional slots")
    print(f"  Total derived: {derived_count}")
    print(f"  Remaining unknown: {unknown_count}")
    
    # Create output directory
    os.makedirs('L15/anchors_plus_tail', exist_ok=True)
    
    # Save results
    with open('L15/anchors_plus_tail/PT_PARTIAL.txt', 'w') as f:
        f.write(plaintext)
    
    with open('L15/anchors_plus_tail/COUNTS.json', 'w') as f:
        json.dump({
            'derived_count': derived_count,
            'unknown_count': unknown_count,
            'tail_forced': tail_forced
        }, f, indent=2)
    
    with open('L15/anchors_plus_tail/TAIL_COVERAGE.json', 'w') as f:
        json.dump({
            'tail_size': 23,
            'slots_forced_by_tail': tail_forced,
            'total_derived_with_tail': derived_count,
            'remaining_unknown': unknown_count,
            'complete': unknown_count == 0
        }, f, indent=2)
    
    return derived_count, unknown_count

def main():
    """Run L=15 test"""
    print("\n" + "="*60)
    print("L=15 ALGEBRA TEST (No Semantics)")
    print("="*60)
    
    # Phase 1: Anchors only
    wheels, derived1, unknown1 = phase1_anchors_only()
    
    # Phase 2: Add tail
    derived2, unknown2 = phase2_add_tail(wheels)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"\nL=15 with anchors only:")
    print(f"  Derived: {derived1}/97")
    print(f"  Unknown: {unknown1}/97")
    
    print(f"\nL=15 with anchors + tail:")
    print(f"  Derived: {derived2}/97")
    print(f"  Unknown: {unknown2}/97")
    
    if unknown2 == 0:
        print("\n✓ SUFFICIENT: Anchors + tail fully determine all 97 positions under L=15")
    else:
        print(f"\n✗ INSUFFICIENT: {unknown2} positions remain unknown even with tail")

if __name__ == "__main__":
    main()