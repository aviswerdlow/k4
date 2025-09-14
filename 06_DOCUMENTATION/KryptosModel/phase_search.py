#!/usr/bin/env python3
"""
Comprehensive phase and orientation search with CT reversal
Searches all combinations to find one with zero bad XOR results
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libk4'))

from alphabets_fixed import code5_A1Z26
from tableau_builder import build_xor_keystream

# K4 ciphertext body
k4_body = "UOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# CRITICAL: Reverse the CT body before XOR (as per spec)
ct_body = k4_body[::-1]

print("COMPREHENSIVE PHASE AND ORIENTATION SEARCH")
print("=" * 60)
print(f"Original CT body (first 31): {k4_body[:31]}")
print(f"Reversed CT body (first 31): {ct_body[:31]}")
print()


def bad_count_for(keystream):
    """Count positions where XOR gives 27-31"""
    bad = 0
    bad_positions = []

    for i, c in enumerate(ct_body):
        rc = code5_A1Z26(c)
        rk = code5_A1Z26(keystream[i])
        r = rc ^ rk

        if r >= 27:
            bad += 1
            if len(bad_positions) < 5:  # Track first few
                bad_positions.append((i, c, keystream[i], r))

    return bad, bad_positions


print("Searching all combinations...")
print("-" * 60)

candidates = []
tested = 0

# Test all combinations
for v_reversed in [True, False]:
    for phase in range(93):  # Test all 93 phases
        keystream = build_xor_keystream(reverse_v=v_reversed, phase=phase)
        bad, bad_pos = bad_count_for(keystream)
        candidates.append((v_reversed, phase, bad, bad_pos))
        tested += 1

        # Print progress every 31 tests
        if tested % 31 == 0:
            print(f"Tested {tested} configurations...")

        # If we find a perfect candidate, report immediately
        if bad == 0:
            print(f"\n✓✓✓ FOUND PERFECT CONFIGURATION!")
            print(f"  V reversed: {v_reversed}")
            print(f"  Phase: {phase}")
            print(f"  Bad count: 0")
            print(f"  Keystream (first 31): {keystream[:31]}")

# Sort by bad count
candidates.sort(key=lambda x: x[2])

print(f"\nTotal configurations tested: {tested}")
print(f"\nBest 10 configurations:")
print("-" * 60)

for i, (v_rev, phase, bad, bad_pos) in enumerate(candidates[:10]):
    print(f"{i+1}. V_rev={v_rev}, phase={phase:2d}: {bad:2d} bad positions")
    if bad > 0 and bad_pos:
        pos, ct, key, r = bad_pos[0]
        print(f"   First bad: pos {pos}, '{ct}' ^ '{key}' = {r}")

# Check if any configuration is perfect
min_bad = candidates[0][2]
if min_bad == 0:
    print("\n✓ At least one configuration produces valid XOR results!")
    print("Next step: Test round-trip with this configuration")
else:
    print(f"\n✗ No configuration eliminates bad XOR results")
    print(f"Minimum bad positions: {min_bad}")
    print("\nIMPLICATION: Either:")
    print("1. The tableau row construction is wrong")
    print("2. The 5-bit XOR interpretation is wrong")
    print("3. Need to try mod-26 operations instead")

# Also try with different row shifts
print("\n" + "=" * 60)
print("TESTING ALTERNATIVE ROW SHIFTS")
print("=" * 60)

# Try using different shifts for the rows
TOP = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# Test if X, V, T should use different shifts
alt_configs = [
    (0, 0, 0, "All rows shift 0"),
    (1, 1, 1, "All rows shift 1"),
    (TOP.index('X'), TOP.index('V'), TOP.index('T'), "Default shifts"),
    (0, TOP.index('V'), 0, "Only V shifted"),
]

print("Testing alternative tableau shifts...")
for sx, sv, st, desc in alt_configs:
    # Just test phase 0, V reversed for quick check
    from tableau_builder import row_window
    row_x = row_window('X', sx, 31)
    row_v = row_window('V', sv, 31)[::-1]
    row_t = row_window('T', st, 31)
    keystream = row_x + row_v + row_t

    bad, _ = bad_count_for(keystream)
    print(f"  {desc}: {bad} bad positions")
    if bad == 0:
        print(f"    ✓ This shift configuration works!")
        print(f"    Row X (shift {sx}): {row_x}")
        print(f"    Row V (shift {sv}, rev): {row_v}")
        print(f"    Row T (shift {st}): {row_t}")