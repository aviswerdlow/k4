#!/usr/bin/env python3
"""
Test with actual Kryptos right panel rows
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libk4'))

from alphabets_fixed import code5_A1Z26

# K4 ciphertext body
k4_body = "UOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# These are the actual text rows from the Kryptos sculpture right panel
# From various sources documenting the sculpture
ACTUAL_ROW1 = "VFPJUDEEHZWETZYVGWHKKQETGFQJNCE"  # 31 chars
ACTUAL_ROW2 = "ATCUUTTAABECEEEEEETTTTPSHLDPNNY"  # 31 chars or similar
ACTUAL_ROW3 = "OHCGSNCRDDTOEPAAVCDEIVNHLTOBIBR"  # 31 chars or similar

# Or perhaps the tableau-style rows as suggested in the brief
TABLEAU_X = "XWXZKRYPTOSABCDEFGHIJLMNQUVWXZK"
TABLEAU_V = "VWXZKRYPTOSABCDEFGHIJLMNQUVWXZK"
TABLEAU_T = "TNQUVWXZKRYPTOSABCDEFGHIJLMNQUV"

print("Testing different panel row possibilities")
print("=" * 60)

def test_keystream(name, keystream):
    """Test a keystream for XOR validity"""
    bad_count = 0
    first_bad = None

    for i in range(min(len(k4_body), len(keystream))):
        ct_char = k4_body[i]
        key_char = keystream[i]

        rc = code5_A1Z26(ct_char)
        rk = code5_A1Z26(key_char)
        r = rc ^ rk

        if r >= 27:
            bad_count += 1
            if first_bad is None:
                first_bad = (i, ct_char, key_char, r)

    print(f"\n{name}:")
    print(f"  Length: {len(keystream)}")
    print(f"  Bad positions: {bad_count}")
    if first_bad:
        i, ct, k, r = first_bad
        print(f"  First bad: pos {i}, '{ct}' ^ '{k}' = {r}")
    else:
        print(f"  ✓ All XOR results valid (0-26)!")

    return bad_count == 0

# Test tableau rows
print("\nTableau-based rows:")
test_keystream("X+V_rev+T", TABLEAU_X + TABLEAU_V[::-1] + TABLEAU_T)
test_keystream("X+V+T", TABLEAU_X + TABLEAU_V + TABLEAU_T)
test_keystream("X_rev+V+T", TABLEAU_X[::-1] + TABLEAU_V + TABLEAU_T)

# Perhaps the brief meant these are the panel keys directly?
# Let me also check if maybe we should use the rows as-is from K1-K3 solutions
K1_PANEL = "VFPJUDEEHZWETZYVGWHKKQETGFQJNCE"  # 31 chars
K2_PANEL = "PFSCZZRLFCUOACDJMVMSPDFOIUYANDS"  # 31 chars
K3_PANEL = "OHCNSCDTGEUAAIYREBRTAWXVUIENLNN"  # 31 chars

print("\nK1-K3 derived panel rows:")
keystream_k123 = K1_PANEL + K2_PANEL + K3_PANEL
if len(keystream_k123) == 93:
    if test_keystream("K1+K2+K3", keystream_k123):
        print("\n✓✓✓ FOUND WORKING KEYSTREAM!")
        print(f"Row 1: {K1_PANEL}")
        print(f"Row 2: {K2_PANEL}")
        print(f"Row 3: {K3_PANEL}")

# Also try with one reversed
test_keystream("K1+K2_rev+K3", K1_PANEL + K2_PANEL[::-1] + K3_PANEL)
test_keystream("K1_rev+K2+K3", K1_PANEL[::-1] + K2_PANEL + K3_PANEL)