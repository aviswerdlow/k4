#!/usr/bin/env python3
"""
Manual verification of TRUE@8 L=11 p=0
Debug why this shows 26 position gains
"""

MASTER_SEED = 1337

def verify_true_placement():
    """Manually verify TRUE@8 with L=11 phase=0"""
    
    # Load ciphertext
    with open('../../02_DATA/ciphertext_97.txt', 'r') as f:
        ciphertext = f.read().strip()
    
    # Known anchors
    anchors = {
        21: 'E', 22: 'A', 23: 'S', 24: 'T',
        25: 'N', 26: 'O', 27: 'R', 28: 'T',
        29: 'H', 30: 'E', 31: 'A', 32: 'S', 33: 'T',
        63: 'B', 64: 'E', 65: 'R', 66: 'L', 67: 'I', 68: 'N',
        69: 'C', 70: 'L', 71: 'O', 72: 'C', 73: 'K'
    }
    
    # Test parameters
    token = "TRUE"
    start = 8
    L = 11
    phase = 0
    
    print(f"=== Verifying {token}@{start} L={L} phase={phase} ===\n")
    print(f"Ciphertext at {start}-{start+3}: {ciphertext[start:start+4]}")
    print(f"Proposed plaintext: {token}\n")
    
    # Family vector (baseline B,V,B,V,B,V)
    family_by_class = {
        0: 'beaufort',
        1: 'vigenere',
        2: 'beaufort',
        3: 'vigenere',
        4: 'beaufort',
        5: 'vigenere'
    }
    
    def compute_class(i):
        return ((i % 2) * 3) + (i % 3)
    
    def compute_residue(c_val, p_val, family):
        if family == 'vigenere':
            return (c_val - p_val) % 26
        elif family == 'beaufort':
            return (p_val - c_val) % 26
        else:
            raise ValueError(f"Unknown family: {family}")
    
    # Build baseline wheels from anchors
    print("Building baseline wheels from anchors...")
    wheels = {}
    for c in range(6):
        wheels[c] = {
            'family': family_by_class[c],
            'slots': {}
        }
    
    anchor_count = 0
    for pos, pt_char in anchors.items():
        c = compute_class(pos)
        s = (pos - phase) % L
        
        ct_char = ciphertext[pos]
        c_val = ord(ct_char) - ord('A')
        p_val = ord(pt_char) - ord('A')
        
        k_req = compute_residue(c_val, p_val, wheels[c]['family'])
        
        if s in wheels[c]['slots']:
            if wheels[c]['slots'][s] != k_req:
                print(f"  ERROR: Anchor conflict at pos {pos}!")
        else:
            wheels[c]['slots'][s] = k_req
            anchor_count += 1
    
    print(f"  Added {anchor_count} constraints from {len(anchors)} anchors\n")
    
    # Show wheel coverage
    print("Baseline wheel coverage:")
    for c in range(6):
        filled = len(wheels[c]['slots'])
        total_slots = L
        print(f"  Class {c} ({wheels[c]['family']}): {filled}/{total_slots} slots filled")
    
    # Now test adding TRUE at position 8
    print(f"\nTesting {token} at positions {start}-{start+3}:")
    conflicts = []
    new_constraints = []
    
    for i, pt_char in enumerate(token):
        pos = start + i
        c = compute_class(pos)
        s = (pos - phase) % L
        
        ct_char = ciphertext[pos]
        c_val = ord(ct_char) - ord('A')
        p_val = ord(pt_char) - ord('A')
        
        k_req = compute_residue(c_val, p_val, wheels[c]['family'])
        
        print(f"  Pos {pos}: CT={ct_char} PT={pt_char} Class={c} Slot={s} K_req={k_req}")
        
        # Check Option-A
        if wheels[c]['family'] in ['vigenere', 'variant-beaufort'] and k_req == 0:
            print(f"    WARNING: Option-A violation (K=0 for additive family)")
            conflicts.append(f"optionA@{pos}")
        
        # Check consistency
        if s in wheels[c]['slots']:
            if wheels[c]['slots'][s] != k_req:
                print(f"    CONFLICT: Slot {s} already has K={wheels[c]['slots'][s]}, needs K={k_req}")
                conflicts.append(f"slot_conflict(c={c},s={s})")
            else:
                print(f"    OK: Matches existing constraint")
        else:
            print(f"    NEW: Would add constraint K={k_req} to slot {s}")
            new_constraints.append((c, s, k_req))
    
    if conflicts:
        print(f"\nREJECTED: {len(conflicts)} conflicts found")
        for conf in conflicts:
            print(f"  - {conf}")
    else:
        print(f"\nACCEPTED: No conflicts, adds {len(new_constraints)} new constraints")
        
        # Add the new constraints
        for c, s, k in new_constraints:
            wheels[c]['slots'][s] = k
        
        # Calculate propagation
        print("\nPropagation analysis:")
        unknown_positions = [i for i in range(97) if i not in anchors]
        can_determine = 0
        
        for pos in unknown_positions:
            c = compute_class(pos)
            s = (pos - phase) % L
            
            if s in wheels[c]['slots']:
                can_determine += 1
        
        print(f"  Unknown positions: {len(unknown_positions)}")
        print(f"  Can determine after adding {token}: {can_determine}")
        print(f"  Gains: {can_determine} positions")
        
        # Show which positions would be determined
        print("\nPositions that would be determined:")
        determined = []
        for pos in range(97):
            if pos in anchors:
                continue
            c = compute_class(pos)
            s = (pos - phase) % L
            if s in wheels[c]['slots']:
                determined.append(pos)
        
        print(f"  {determined[:20]}...")
        print(f"  Total: {len(determined)} positions")
        
        # Verify the gain calculation
        # How many could we determine before adding TRUE?
        baseline_wheels = {}
        for c in range(6):
            baseline_wheels[c] = {'slots': {}}
        
        for pos, pt_char in anchors.items():
            c = compute_class(pos)
            s = (pos - phase) % L
            ct_char = ciphertext[pos]
            c_val = ord(ct_char) - ord('A')
            p_val = ord(pt_char) - ord('A')
            k_req = compute_residue(c_val, p_val, family_by_class[c])
            baseline_wheels[c]['slots'][s] = k_req
        
        baseline_determined = 0
        for pos in unknown_positions:
            c = compute_class(pos)
            s = (pos - phase) % L
            if s in baseline_wheels[c]['slots']:
                baseline_determined += 1
        
        print(f"\nGain verification:")
        print(f"  Baseline (anchors only): {baseline_determined} positions")
        print(f"  After adding {token}: {can_determine} positions")
        print(f"  Net gain: {can_determine - baseline_determined} positions")

if __name__ == "__main__":
    print(f"MASTER_SEED: {MASTER_SEED}\n")
    verify_true_placement()