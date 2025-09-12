#!/usr/bin/env python3
"""
E5 - Tail-first Reverse Engineering
Work backwards from tail to see if it provides extra constraints
"""

import json
import os
import hashlib
from typing import Dict, List, Optional, Set

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

def build_tail_first_wheels():
    """Build wheels starting from tail positions first"""
    L = 17
    wheels = {}
    
    for c in range(6):
        wheels[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L,
            'residues': [None] * L,
            'sources': [set() for _ in range(L)]  # Track where each residue came from
        }
    
    return wheels

def fill_from_tail(ciphertext, canonical_pt, tail, wheels):
    """Fill wheel residues from tail positions first"""
    L = 17
    tail_constraints = []
    
    for pos in tail:
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
        
        # Record constraint
        tail_constraints.append({
            'pos': pos,
            'class': c,
            'slot': s,
            'key': k_val
        })
        
        # Fill wheel
        if wheels[c]['residues'][s] is None:
            wheels[c]['residues'][s] = k_val
            wheels[c]['sources'][s].add(f'tail_{pos}')
        elif wheels[c]['residues'][s] != k_val:
            # Conflict!
            wheels[c]['sources'][s].add(f'conflict_tail_{pos}')
    
    return tail_constraints

def propagate_from_tail(wheels, tail_constraints):
    """See if tail constraints propagate to head positions"""
    L = 17
    propagated = []
    
    # Check which head positions share slots with tail
    for head_pos in range(74):  # Head is 0-73
        c = compute_class_baseline(head_pos)
        s = head_pos % L
        
        # Does this slot have a value from tail?
        if wheels[c]['residues'][s] is not None:
            # Found a propagation!
            propagated.append({
                'head_pos': head_pos,
                'class': c,
                'slot': s,
                'key': wheels[c]['residues'][s],
                'source': list(wheels[c]['sources'][s])
            })
    
    return propagated

def fill_from_anchors(ciphertext, canonical_pt, anchors, wheels):
    """Fill remaining slots from anchor positions"""
    L = 17
    anchor_constraints = []
    
    for pos in anchors:
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
        
        # Record constraint
        anchor_constraints.append({
            'pos': pos,
            'class': c,
            'slot': s,
            'key': k_val
        })
        
        # Fill wheel if empty
        if wheels[c]['residues'][s] is None:
            wheels[c]['residues'][s] = k_val
            wheels[c]['sources'][s].add(f'anchor_{pos}')
        elif wheels[c]['residues'][s] != k_val:
            # Conflict with tail!
            wheels[c]['sources'][s].add(f'conflict_anchor_{pos}')
    
    return anchor_constraints

def derive_plaintext(ciphertext, wheels):
    """Derive plaintext using filled wheels"""
    L = 17
    derived = []
    
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
    
    return ''.join(derived)

def analyze_tail_patterns(tail_constraints):
    """Analyze patterns in tail-derived keys"""
    patterns = {
        'unique_slots': set(),
        'key_distribution': {},
        'class_coverage': {c: set() for c in range(6)}
    }
    
    for constraint in tail_constraints:
        patterns['unique_slots'].add((constraint['class'], constraint['slot']))
        
        key = constraint['key']
        if key not in patterns['key_distribution']:
            patterns['key_distribution'][key] = 0
        patterns['key_distribution'][key] += 1
        
        patterns['class_coverage'][constraint['class']].add(constraint['slot'])
    
    return patterns

def main():
    """Run E5 tail-first tests"""
    print("=== E5: Tail-first Reverse Engineering ===\n")
    
    os.makedirs('E5_tail_first', exist_ok=True)
    
    # Load data
    ciphertext, canonical_pt, anchors, tail = load_data()
    
    print("Working backwards from tail positions...")
    print(f"Tail: positions {tail[0]}-{tail[-1]} ({len(tail)} letters)")
    print(f"Tail text: {canonical_pt[tail[0]:tail[-1]+1]}\n")
    
    # Build wheels tail-first
    wheels = build_tail_first_wheels()
    
    # Step 1: Fill from tail
    print("Step 1: Extracting constraints from tail...")
    tail_constraints = fill_from_tail(ciphertext, canonical_pt, tail, wheels)
    print(f"  Tail provides {len(tail_constraints)} constraints")
    
    # Analyze tail patterns
    patterns = analyze_tail_patterns(tail_constraints)
    print(f"  Unique (class,slot) pairs: {len(patterns['unique_slots'])}")
    print(f"  Key value distribution: {len(patterns['key_distribution'])} unique values")
    
    # Step 2: Check propagation
    print("\nStep 2: Checking propagation to head...")
    propagated = propagate_from_tail(wheels, tail_constraints)
    print(f"  Tail constraints propagate to {len(propagated)} head positions")
    
    if propagated:
        print("  Sample propagations:")
        for p in propagated[:5]:
            print(f"    Position {p['head_pos']}: gets key {p['key']} from {p['source']}")
    
    # Step 3: Fill from anchors
    print("\nStep 3: Adding anchor constraints...")
    anchor_constraints = fill_from_anchors(ciphertext, canonical_pt, anchors, wheels)
    print(f"  Anchors provide {len(anchor_constraints)} constraints")
    
    # Check for conflicts
    conflicts = 0
    for c in range(6):
        for s in range(17):
            sources = wheels[c]['sources'][s]
            if any('conflict' in str(src) for src in sources):
                conflicts += 1
    
    print(f"  Conflicts detected: {conflicts}")
    
    # Step 4: Derive plaintext
    print("\nStep 4: Deriving plaintext...")
    derived_pt = derive_plaintext(ciphertext, wheels)
    unknowns = derived_pt.count('?')
    
    print(f"  Unknown positions: {unknowns}")
    
    # Verify constraints
    valid = True
    for i in anchors + tail:
        if derived_pt[i] != canonical_pt[i]:
            valid = False
            break
    
    print(f"  Constraints preserved: {valid}")
    
    # Analysis
    print("\n=== Analysis ===")
    
    # Count how many slots are filled by tail vs anchors
    tail_filled = 0
    anchor_filled = 0
    both_filled = 0
    unfilled = 0
    
    for c in range(6):
        for s in range(17):
            sources = wheels[c]['sources'][s]
            has_tail = any('tail' in str(src) for src in sources)
            has_anchor = any('anchor' in str(src) for src in sources)
            
            if has_tail and has_anchor:
                both_filled += 1
            elif has_tail:
                tail_filled += 1
            elif has_anchor:
                anchor_filled += 1
            else:
                unfilled += 1
    
    total_slots = 6 * 17
    print(f"Total wheel slots: {total_slots}")
    print(f"  Filled by tail only: {tail_filled}")
    print(f"  Filled by anchors only: {anchor_filled}")
    print(f"  Filled by both: {both_filled}")
    print(f"  Unfilled: {unfilled}")
    
    print(f"\nTail-first approach:")
    if unknowns < 50:
        print(f"  SUCCESS: Reduced unknowns from 50 to {unknowns}")
    else:
        print(f"  No improvement: Still {unknowns} unknowns")
        print("  Tail doesn't provide extra constraints beyond standard L=17")
    
    # Save results
    results = {
        'test': 'Tail-first reverse engineering',
        'tail_constraints': len(tail_constraints),
        'propagated_to_head': len(propagated),
        'conflicts': conflicts,
        'unknowns': unknowns,
        'valid': valid,
        'slot_coverage': {
            'tail_only': tail_filled,
            'anchor_only': anchor_filled,
            'both': both_filled,
            'unfilled': unfilled
        },
        'conclusion': 'No extra constraints from tail' if unknowns == 50 else f'Reduced to {unknowns} unknowns'
    }
    
    with open('E5_tail_first/RESULT.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    with open('E5_tail_first/plaintext_derived.txt', 'w') as f:
        f.write(derived_pt)
    
    print("\nResults saved to E5_tail_first/")

if __name__ == "__main__":
    main()