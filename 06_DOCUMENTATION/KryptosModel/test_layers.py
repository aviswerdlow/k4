#!/usr/bin/env python3
"""
Debug the K4 two-layer system step by step
"""

from libk4.alphabets import encode5, decode5, c2i25, i2c25, c2i26, i2c26, ALPH25, ALPH26
from libk4.mask_base5 import base5_mask, base5_unmask
from libk4.xor5 import xor5_passthrough, xor5_passthrough_decrypt

# Known K4 ciphertext (without OBKR header)
k4_body = "UOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Panel row keys
keys = [
    "VFPJUDEEHZWETZYVGWHKKQETGFQJNCE",  # Row 1
    "PFSCZZRLFCUOACDJMVMSPDFOIUYANDS",  # Row 2
    "OHCNSCDTGEUAAIYREBRTAWXVUIENLNN"   # Row 3
]

print("=" * 60)
print("K4 LAYER-BY-LAYER ANALYSIS")
print("=" * 60)

# Build full XOR key for 93 positions
xor_key_full = ""
for row in range(3):
    xor_key_full += keys[row][:31]
xor_key_full = xor_key_full[:93]  # Ensure exactly 93 chars

print(f"\nCiphertext body: {k4_body}")
print(f"Length: {len(k4_body)}")

# Convert CT to 5-bit values (26-letter alphabet)
ct_values = encode5(k4_body, alphabet='26')
print(f"\nCT as 5-bit values (first 10): {ct_values[:10]}")

# Get XOR key values
xor_values = encode5(xor_key_full, alphabet='26')
print(f"XOR key values (first 10): {xor_values[:10]}")

# Apply Layer B inverse (XOR with pass-through)
after_xor = xor5_passthrough_decrypt(ct_values, xor_values)
print(f"\nAfter XOR inverse (first 10): {after_xor[:10]}")

# The values after XOR should be in 25-letter range for base-5 unmask
# Let's check if any are out of range
out_of_range = [v for v in after_xor if v >= 25]
if out_of_range:
    print(f"WARNING: {len(out_of_range)} values out of 25-letter range")
    print(f"Out of range values: {out_of_range[:10]}...")

    # Try reducing to 25-letter range
    after_xor_25 = [v % 25 for v in after_xor]
    print(f"After mod 25 (first 10): {after_xor_25[:10]}")
else:
    after_xor_25 = after_xor

# Apply Layer A inverse (base-5 unmask) with CIAX key
mask_key = "CIAX"
plaintext = base5_unmask(after_xor_25, mask_key)
print(f"\nDecrypted plaintext: {plaintext}")

# Check for anchors
if "BERLIN" in plaintext:
    idx = plaintext.index("BERLIN")
    print(f"✓ BERLIN found at position {idx}")
    print(f"  Context: ...{plaintext[max(0,idx-5):idx+11]}...")
else:
    # Check what's at position 63-69
    print(f"✗ BERLIN not found")
    print(f"  At pos 63-69: {plaintext[63:69]}")

if "CLOCK" in plaintext:
    idx = plaintext.index("CLOCK")
    print(f"✓ CLOCK found at position {idx}")
    print(f"  Context: ...{plaintext[max(0,idx-5):idx+10]}...")
else:
    # Check what's at position 69-74
    print(f"✗ CLOCK not found")
    print(f"  At pos 69-74: {plaintext[69:74]}")

print("\n" + "=" * 60)
print("REVERSE TEST: Known plaintext fragment")
print("=" * 60)

# Test with a known plaintext that should appear (use A instead of X)
test_pt = "A" * 63 + "BERLIN" + "CLOCK" + "A" * 20  # Put BERLIN and CLOCK at right positions
test_pt = test_pt[:93]  # Ensure 93 chars

print(f"Test plaintext: {test_pt[:20]}...{test_pt[60:80]}...")

# Forward encryption
# Layer A: Base-5 mask
masked = base5_mask(test_pt, mask_key)
print(f"After base-5 mask (positions 63-74): {masked[63:74]}")

# Layer B: XOR
encrypted = xor5_passthrough(masked, xor_values)
print(f"After XOR (positions 63-74): {encrypted[63:74]}")

# Convert to text
ct_text = decode5(encrypted, alphabet='26')
print(f"Ciphertext: {ct_text}")

# Compare with actual K4 at those positions
print(f"Actual K4 at 63-74: {k4_body[63:74]}")
print(f"Generated at 63-74: {ct_text[63:74]}")