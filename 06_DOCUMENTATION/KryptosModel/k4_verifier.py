#!/usr/bin/env python3
"""
K4 Cryptosystem Verifier
Tests the two-layer XOR + base-5 mask implementation
"""

import sys
from libk4 import K4Cipher


def main():
    """Run verification tests on K4 cryptosystem"""

    print("=" * 60)
    print("K4 CRYPTOSYSTEM VERIFIER")
    print("Two-layer: XOR (Layer B) + Base-5 Mask (Layer A)")
    print("=" * 60)

    # Known K4 ciphertext
    k4_ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

    # Initialize cipher with default keys
    cipher = K4Cipher(mask_key="CIAX")

    print("\nConfiguration:")
    print(f"  Mask Key (Layer A): {cipher.mask_key}")
    print(f"  XOR Keys (Layer B):")
    for i, key in enumerate(cipher.xor_keys, 1):
        print(f"    Row {i}: {key} ({len(key)} chars)")

    print("\n" + "-" * 60)
    print("TEST 1: Decrypt K4 ciphertext")
    print("-" * 60)

    # Decrypt the known K4 ciphertext
    plaintext = cipher.decrypt(k4_ct)
    print(f"Ciphertext: {k4_ct}")
    print(f"Decrypted:  {plaintext}")

    # Check for known anchors
    if "BERLIN" in plaintext[63:69]:
        print("✓ BERLIN found at position 63-69")
    else:
        print("✗ BERLIN not found at expected position")

    if "CLOCK" in plaintext[69:74]:
        print("✓ CLOCK found at position 69-74")
    else:
        print("✗ CLOCK not found at expected position")

    print("\n" + "-" * 60)
    print("TEST 2: Round-trip verification")
    print("-" * 60)

    success, details = cipher.verify_roundtrip()

    print(f"Decrypted text: {details['decrypted']}")
    print(f"Re-encrypted:   {details['re_encrypted']}")
    print(f"Original CT:    {details['ciphertext']}")
    print(f"Match: {'✓ YES' if details['match'] else '✗ NO'}")

    print("\n" + "-" * 60)
    print("TEST 3: Custom plaintext test")
    print("-" * 60)

    # Test with a simple message
    test_pt = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOGTHEQUICKBROWNFOXJUMPSOVERTHELAZYDOGTHEQUICKBROWNFOXJUMPS"
    print(f"Test plaintext: {test_pt}")

    encrypted = cipher.encrypt(test_pt)
    decrypted = cipher.decrypt(encrypted)

    print(f"Encrypted:      {encrypted}")
    print(f"Decrypted:      {decrypted}")
    print(f"Round-trip OK:  {'✓ YES' if decrypted == test_pt else '✗ NO'}")

    print("\n" + "-" * 60)
    print("TEST 4: Layer analysis")
    print("-" * 60)

    # Show intermediate values for first few characters
    test_text = "BERLIN"
    print(f"Analyzing: {test_text}")

    from libk4.alphabets import c2i25, encode5
    from libk4.mask_base5 import base5_mask

    # Layer A: Base-5 mask
    masked = base5_mask(test_text, cipher.mask_key)
    print(f"After Layer A (base-5 mask): {masked}")

    # Layer B: XOR
    xor_keys = [cipher._get_xor_key_for_position(i) for i in range(len(masked))]
    print(f"XOR key values: {xor_keys}")

    from libk4.xor5 import xor5_passthrough
    final = xor5_passthrough(masked, xor_keys)
    print(f"After Layer B (XOR): {final}")

    from libk4.alphabets import decode5
    ct_chars = decode5(final, alphabet='26')
    print(f"Final ciphertext: {ct_chars}")

    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)

    # Return success status
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())