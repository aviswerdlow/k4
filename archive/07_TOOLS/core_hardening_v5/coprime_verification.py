#!/usr/bin/env python3
"""
Verify the co-prime property: with L=17 and 97 positions,
each (class, slot) pair appears exactly once.
"""

import math
from collections import defaultdict

def compute_class_baseline(i):
    """Baseline class function: ((i%2)*3)+(i%3)"""
    return ((i % 2) * 3) + (i % 3)

def verify_coprime_property(L=17):
    """
    Verify that with L=17, each of 97 positions maps to unique (class,slot).
    This happens when gcd(L, 97) = 1 and the class pattern doesn't interfere.
    """
    print(f"\n=== Co-prime Property Verification ===")
    print(f"L = {L}, Positions = 97")
    print(f"gcd({L}, 97) = {math.gcd(L, 97)}")
    
    # Map each position to (class, slot)
    position_to_slot = {}
    slot_to_positions = defaultdict(list)
    
    for i in range(97):
        c = compute_class_baseline(i)
        s = i % L
        position_to_slot[i] = (c, s)
        slot_to_positions[(c, s)].append(i)
    
    # Check uniqueness
    unique_slots = len(slot_to_positions)
    max_positions_per_slot = max(len(positions) for positions in slot_to_positions.values())
    
    print(f"\nResults:")
    print(f"  Unique (class, slot) pairs: {unique_slots}")
    print(f"  Max positions per slot: {max_positions_per_slot}")
    
    if unique_slots == 97 and max_positions_per_slot == 1:
        print(f"  ✓ Perfect 1-to-1 mapping: each position has unique (class, slot)")
    else:
        print(f"  ✗ Not 1-to-1 mapping")
        
    # Show slots with multiple positions (if any)
    duplicates = [(slot, positions) for slot, positions in slot_to_positions.items() 
                  if len(positions) > 1]
    if duplicates:
        print(f"\n  Slots with multiple positions:")
        for slot, positions in duplicates[:5]:
            print(f"    {slot}: {positions}")
    
    return unique_slots == 97, slot_to_positions

def analyze_implications():
    """
    Analyze what the 1-to-1 mapping means for set-cover.
    """
    print(f"\n=== Implications for Set-Cover ===")
    
    is_one_to_one, slot_map = verify_coprime_property(17)
    
    if is_one_to_one:
        print(f"\nKey Insight:")
        print(f"  With L=17 and 97 positions, each position determines a unique slot.")
        print(f"  Therefore:")
        print(f"    - 24 anchor positions → 24 unique slots determined")
        print(f"    - 73 remaining positions → 73 unique slots to determine")
        print(f"    - Minimal set-cover size = 73 (need ALL remaining positions)")
        print(f"\nThis means:")
        print(f"  • No subset smaller than 73 can complete the solution")
        print(f"  • The 23-position tail can only cover 23 of 73 needed slots")
        print(f"  • 50 additional positions beyond tail would be needed")
    
    return is_one_to_one

def test_alternative_L_values():
    """
    Test if other L values might reduce unknowns.
    """
    print(f"\n=== Testing Alternative L Values ===")
    
    results = []
    
    for L in [11, 13, 15, 17, 19, 23, 29]:
        # Get anchor positions
        anchor_indices = []
        for start, end in [(21, 25), (25, 34), (63, 69), (69, 74)]:
            anchor_indices.extend(range(start, end))
        
        # Map positions to slots
        anchor_slots = set()
        for i in anchor_indices:
            c = compute_class_baseline(i)
            s = i % L
            anchor_slots.add((c, s))
        
        # Count how many total positions these slots cover
        all_slots = defaultdict(list)
        for i in range(97):
            c = compute_class_baseline(i)
            s = i % L
            all_slots[(c, s)].append(i)
        
        covered_positions = set()
        for slot in anchor_slots:
            if slot in all_slots:
                covered_positions.update(all_slots[slot])
        
        unknown = 97 - len(covered_positions)
        
        results.append({
            'L': L,
            'gcd_97': math.gcd(L, 97),
            'anchor_slots': len(anchor_slots),
            'covered_positions': len(covered_positions),
            'unknown_positions': unknown,
            'unique_slots': len(all_slots),
            'max_per_slot': max(len(v) for v in all_slots.values())
        })
        
        print(f"\nL={L}:")
        print(f"  gcd(L, 97) = {math.gcd(L, 97)}")
        print(f"  Unique slots used: {len(all_slots)}")
        print(f"  Max positions/slot: {max(len(v) for v in all_slots.values())}")
        print(f"  Anchors cover: {len(covered_positions)} positions")
        print(f"  Unknown: {unknown} positions")
    
    # Find best L
    best = min(results, key=lambda x: x['unknown_positions'])
    print(f"\nBest L value: {best['L']} with {best['unknown_positions']} unknowns")
    
    if best['L'] == 17:
        print("✓ L=17 is optimal (or tied) for minimizing unknowns")
    else:
        print(f"✗ L={best['L']} would be better than L=17")
    
    return results

def main():
    """Run complete co-prime analysis"""
    print("\n=== Core-Hardening v5: Co-prime Analysis ===")
    
    # Verify the co-prime property
    is_one_to_one = analyze_implications()
    
    # Test alternatives
    results = test_alternative_L_values()
    
    # Save results
    import json
    with open('COPRIME_ANALYSIS.json', 'w') as f:
        json.dump({
            'L_17_is_one_to_one': is_one_to_one,
            'minimal_set_cover_size': 73 if is_one_to_one else None,
            'tail_coverage': 23,
            'shortfall': 50 if is_one_to_one else None,
            'alternative_L_results': results
        }, f, indent=2)
    
    print("\n✅ Analysis complete. Saved to COPRIME_ANALYSIS.json")

if __name__ == "__main__":
    main()