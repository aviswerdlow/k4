#!/usr/bin/env python3
"""
Debug XOR operation to find where 27-31 values occur
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libk4'))

from alphabets_fixed import code5_A1Z26

# K4 ciphertext body
k4_body = "UOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Panel rows
ROW_X = "XWXZKRYPTOSABCDEFGHIJLMNQUVWXZK"
ROW_V = "VWXZKRYPTOSABCDEFGHIJLMNQUVWXZK"
ROW_T = "TNQUVWXZKRYPTOSABCDEFGHIJLMNQUV"

# Build keystream (V reversed)
keystream = ROW_X + ROW_V[::-1] + ROW_T

print("XOR Debug Analysis")
print("=" * 60)
print(f"CT body length: {len(k4_body)}")
print(f"Keystream length: {len(keystream)}")
print()

# Find positions where XOR gives 27-31
bad_positions = []
for i in range(len(k4_body)):
    ct_char = k4_body[i]
    key_char = keystream[i]

    rc = code5_A1Z26(ct_char)
    rk = code5_A1Z26(key_char)
    r = rc ^ rk

    if r >= 27:
        bad_positions.append(i)
        print(f"Position {i:2d}: CT='{ct_char}' ({rc:2d}) ^ Key='{key_char}' ({rk:2d}) = {r} ❌")
        if i < 31:
            print(f"  (Row X, char {i})")
        elif i < 62:
            print(f"  (Row V reversed, char {i-31})")
        else:
            print(f"  (Row T, char {i-62})")

print(f"\nTotal bad positions: {len(bad_positions)}")
print(f"Bad positions: {bad_positions[:10]}...")

# Try different orientations
print("\n" + "=" * 60)
print("Testing alternative orientations:")
print("=" * 60)

orientations = [
    ("X-fwd, V-rev, T-fwd", ROW_X, ROW_V[::-1], ROW_T),
    ("X-rev, V-rev, T-fwd", ROW_X[::-1], ROW_V[::-1], ROW_T),
    ("X-fwd, V-fwd, T-fwd", ROW_X, ROW_V, ROW_T),
    ("X-fwd, V-rev, T-rev", ROW_X, ROW_V[::-1], ROW_T[::-1]),
]

for name, x, v, t in orientations:
    test_keystream = x + v + t
    bad_count = 0

    for i in range(len(k4_body)):
        ct_char = k4_body[i]
        key_char = test_keystream[i]

        rc = code5_A1Z26(ct_char)
        rk = code5_A1Z26(key_char)
        r = rc ^ rk

        if r >= 27:
            bad_count += 1

    print(f"{name}: {bad_count} bad positions")
    if bad_count == 0:
        print(f"  ✓ This orientation works!")
        print(f"  Keystream: {test_keystream}")