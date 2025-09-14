#!/usr/bin/env python3
"""
Simple test to understand the cipher requirements
"""

# The brief states:
# 1. Plaintext is 93 chars (25-letter alphabet, no X)
# 2. Ciphertext is 97 chars (OBKR + 93 body) in 26-letter alphabet
# 3. Layer A: base-5 mask with CIAX key
# 4. Layer B: 5-bit XOR with panel keys and pass-through rule

# Known K4 ciphertext
k4_full = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
k4_body = k4_full[4:]  # Remove OBKR

# Known anchors in plaintext
# BERLIN should be at position 63-69
# CLOCK should be at position 69-74

print("K4 Analysis")
print("=" * 60)
print(f"K4 body: {k4_body}")
print(f"Length: {len(k4_body)}")
print(f"At positions 63-69: {k4_body[63:69]}")
print(f"At positions 69-74: {k4_body[69:74]}")

# Panel keys (31 chars each)
panel1 = "VFPJUDEEHZWETZYVGWHKKQETGFQJNCE"
panel2 = "PFSCZZRLFCUOACDJMVMSPDFOIUYANDS"
panel3 = "OHCNSCDTGEUAAIYREBRTAWXVUIENLNN"

print(f"\nPanel 1: {panel1} ({len(panel1)} chars)")
print(f"Panel 2: {panel2} ({len(panel2)} chars)")
print(f"Panel 3: {panel3} ({len(panel3)} chars)")

# The XOR key at positions 63-74 would be from panel 3
# Position 63 is character 63%31 = 1 of panel 3
# Position 69 is character 69%31 = 7 of panel 3
print(f"\nXOR key at pos 63-69: {panel3[1:7]}")
print(f"XOR key at pos 69-74: {panel3[7:12]}")

# Let's think about what values BERLIN and CLOCK would need to produce
# the ciphertext at those positions

from libk4.alphabets import c2i26, i2c26, c2i25, i2c25

print("\n" + "=" * 60)
print("Working backwards from known anchors")
print("=" * 60)

# CT at positions 63-69 is "TTMZFP"
# XOR key is "HCNSCD" (from panel3[1:7])
# After XOR inverse, we should get values that when unmasked give "BERLIN"

ct_berlin = "TTMZFP"
xor_berlin = "HCNSCD"

print(f"CT (63-69): {ct_berlin}")
print(f"XOR key:    {xor_berlin}")

# Convert to 5-bit values
ct_vals = [c2i26(c) for c in ct_berlin]
xor_vals = [c2i26(c) for c in xor_berlin]

print(f"CT values:  {ct_vals}")
print(f"XOR values: {xor_vals}")

# Apply XOR inverse (same as forward since XOR is self-inverse)
# But with pass-through rule: if key bit is 0, value passes through
after_xor = []
for ct_v, xor_v in zip(ct_vals, xor_vals):
    result = 0
    for bit in range(5):
        ct_bit = (ct_v >> bit) & 1
        xor_bit = (xor_v >> bit) & 1

        if xor_bit == 0:
            # Pass through
            result_bit = ct_bit
        else:
            # XOR
            result_bit = ct_bit ^ xor_bit

        result |= (result_bit << bit)

    after_xor.append(result)

print(f"After XOR:  {after_xor}")

# These values need to unmask to BERLIN
# BERLIN in 25-letter alphabet
berlin_vals = [c2i25(c) for c in "BERLIN"]
print(f"BERLIN values (25-letter): {berlin_vals}")

# What mask values would produce after_xor from berlin_vals?
# mask_val = (after_xor - berlin_val) % 25
# But after_xor values might be >25...

# The issue is that XOR produces 5-bit values (0-31) but we need 25-letter values
# Perhaps we need to map differently?

print("\n" + "=" * 60)
print("Alternative: Map 26→25 before unmasking")
print("=" * 60)

# Map 26-letter values to 25-letter by removing X's position
def map_26_to_25(val26):
    """Map 26-letter index to 25-letter (skip X at position 23)"""
    if val26 < 23:  # Before X
        return val26
    else:  # After X
        return val26 - 1

def map_25_to_26(val25):
    """Map 25-letter index to 26-letter (reinsert X at position 23)"""
    if val25 < 23:  # Before where X would be
        return val25
    else:  # After where X would be
        return val25 + 1

# Try mapping after_xor values
after_xor_25 = []
for v in after_xor:
    # If value is in 26-letter range, map it
    if v < 26:
        after_xor_25.append(map_26_to_25(v))
    else:
        # Out of range - need to handle somehow
        after_xor_25.append(v % 25)

print(f"After XOR (mapped to 25): {after_xor_25}")

# Now try to find mask key that produces this
# For CIAX mask key at position 63
mask_key = "CIAX"
mask_vals = [c2i25(c) for c in mask_key]
print(f"Mask key values: {mask_vals}")

# At position 63, we'd use mask_vals[63 % 4] = mask_vals[3] = X
# But X isn't in 25-letter alphabet!
# The brief says to use CIAX but X isn't valid...

print("\nIssue: CIAX contains X which isn't in 25-letter alphabet!")
print("Perhaps the mask key should be different, or interpreted differently?")