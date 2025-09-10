#!/usr/bin/env python3
"""
Quick verification of MERIDIAN@34-41 with L=11
Check if this really provides 21-position gain
"""

MASTER_SEED = 1337

def verify_meridian():
    """Verify the MERIDIAN placement claim"""
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
    
    # Test MERIDIAN at 34-41
    candidate = "MERIDIAN"
    start = 34
    L = 11
    phase = 0  # Changed from 4 to 0
    
    print(f"Testing {candidate} at positions {start}-{start+7}")
    print(f"Period L={L}, Phase={phase}")
    print(f"Ciphertext: {ciphertext[start:start+8]}")
    
    # Build wheels
    wheels = {}
    for w in range(L):
        wheels[w] = {'vigenere': None, 'beaufort': None}
    
    # Add anchors to wheels
    for pos, pt_char in anchors.items():
        slot = (pos - phase) % L  # Should be minus for consistency with f1_anchor_search_v2
        ct_char = ciphertext[pos]
        
        c_val = ord(ct_char) - ord('A')
        p_val = ord(pt_char) - ord('A')
        
        # Vigenere: k = c - p
        k_vig = (c_val - p_val) % 26
        
        # Beaufort: k = p + c
        k_beau = (p_val + c_val) % 26
        
        if wheels[slot]['vigenere'] is None:
            wheels[slot]['vigenere'] = k_vig
        elif wheels[slot]['vigenere'] != k_vig:
            print(f"Conflict at slot {slot} for Vigenere")
        
        if wheels[slot]['beaufort'] is None:
            wheels[slot]['beaufort'] = k_beau
        elif wheels[slot]['beaufort'] != k_beau:
            print(f"Conflict at slot {slot} for Beaufort")
    
    # Add MERIDIAN
    for i, pt_char in enumerate(candidate):
        pos = start + i
        slot = (pos - phase) % L  # Should be minus for consistency
        ct_char = ciphertext[pos]
        
        c_val = ord(ct_char) - ord('A')
        p_val = ord(pt_char) - ord('A')
        
        k_vig = (c_val - p_val) % 26
        k_beau = (p_val + c_val) % 26
        
        print(f"  Pos {pos}: CT={ct_char} PT={pt_char} Slot={slot} K_vig={k_vig} K_beau={k_beau}")
        
        if wheels[slot]['vigenere'] is not None:
            if wheels[slot]['vigenere'] != k_vig:
                print(f"    Vigenere conflict! Expected {wheels[slot]['vigenere']}, got {k_vig}")
        else:
            wheels[slot]['vigenere'] = k_vig
            
        if wheels[slot]['beaufort'] is not None:
            if wheels[slot]['beaufort'] != k_beau:
                print(f"    Beaufort conflict! Expected {wheels[slot]['beaufort']}, got {k_beau}")
        else:
            wheels[slot]['beaufort'] = k_beau
    
    # Count filled slots
    filled_vig = sum(1 for w in wheels.values() if w['vigenere'] is not None)
    filled_beau = sum(1 for w in wheels.values() if w['beaufort'] is not None)
    
    print(f"\nWheel coverage:")
    print(f"  Vigenere: {filled_vig}/{L} slots filled")
    print(f"  Beaufort: {filled_beau}/{L} slots filled")
    
    # Check propagation
    unknowns = [i for i in range(97) if i not in anchors]
    can_determine_vig = 0
    can_determine_beau = 0
    
    for pos in unknowns:
        slot = (pos - phase) % L
        if wheels[slot]['vigenere'] is not None:
            can_determine_vig += 1
        if wheels[slot]['beaufort'] is not None:
            can_determine_beau += 1
    
    print(f"\nPropagation potential:")
    print(f"  Vigenere: Can determine {can_determine_vig} of {len(unknowns)} unknowns")
    print(f"  Beaufort: Can determine {can_determine_beau} of {len(unknowns)} unknowns")
    
    # The "gain" would be positions we can now determine that we couldn't before
    # Since we started with 24 anchors determining some positions
    baseline = len([p for p in unknowns if (p - phase) % L in [
        (a - phase) % L for a in anchors
    ]])
    
    print(f"\nBaseline from anchors alone: ~{baseline} positions")
    print(f"Gain from adding MERIDIAN: {can_determine_vig - baseline} (Vigenere)")

if __name__ == "__main__":
    print("=== Verifying MERIDIAN@34-41 L=11 ===")
    print(f"MASTER_SEED: {MASTER_SEED}\n")
    verify_meridian()