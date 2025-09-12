#!/usr/bin/env python3
"""
Debug why F1 isn't catching MERIDIAN@34 conflicts
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from f1_anchor_search.f1_anchor_search_v2 import AnchorSearcherV2

def debug_meridian34():
    """Trace through MERIDIAN@34 placement"""
    searcher = AnchorSearcherV2()
    
    # Build baseline wheels for L=11 phase=0
    baseline = searcher.build_baseline_wheels(L=11, phase=0)
    
    if baseline is None:
        print("Baseline is invalid!")
        return
    
    print("Baseline wheels (L=11, phase=0):")
    for c in range(6):
        family = baseline[c]['family']
        slots = baseline[c]['slots']
        print(f"  Class {c} ({family}): {len(slots)} slots filled")
        print(f"    Slots: {dict(list(slots.items())[:5])}...")
    
    # Now test MERIDIAN at position 34
    token = "MERIDIAN"
    start = 34
    L = 11
    phase = 0
    
    print(f"\nTesting {token} at {start}:")
    
    for i, char in enumerate(token):
        pos = start + i
        c = searcher.compute_class(pos)
        s = (pos - phase) % L
        
        ct_char = searcher.ciphertext[pos]
        c_val = ord(ct_char) - ord('A')
        p_val = ord(char) - ord('A')
        
        k_req = searcher.compute_residue(c_val, p_val, baseline[c]['family'])
        
        print(f"  Pos {pos}: CT={ct_char} PT={char} Class={c} Slot={s} K_req={k_req}")
        
        # Check if already in anchors
        if pos in searcher.anchors:
            if searcher.anchors[pos] == char:
                print(f"    Matches anchor")
            else:
                print(f"    CONFLICTS with anchor {searcher.anchors[pos]}")
        else:
            # Check consistency
            if s in baseline[c]['slots']:
                existing = baseline[c]['slots'][s]
                if existing == k_req:
                    print(f"    OK: Matches existing K={existing}")
                else:
                    print(f"    CONFLICT: Slot has K={existing}, needs K={k_req}")
            else:
                print(f"    NEW: Would add K={k_req} to slot {s}")

if __name__ == "__main__":
    debug_meridian34()