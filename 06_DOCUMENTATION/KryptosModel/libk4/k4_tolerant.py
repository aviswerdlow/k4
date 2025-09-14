#!/usr/bin/env python3
"""
K4 implementation with tolerance for XOR 27-31 results
Tests with the K1-K3 derived panel rows
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from alphabets_fixed import ALPH25, ALPH26
from mask_base5_fixed import base5_mask_string, base5_unmask_string
from xor5_tolerant import xor5_decrypt_string_tolerant


class K4Tolerant:
    """K4 cipher with XOR tolerance"""

    def __init__(self):
        # Use the panel rows that were in the original attempt
        # (these matched K1-K3 text segments)
        self.ROW_1 = "VFPJUDEEHZWETZYVGWHKKQETGFQJNCE"  # 31 chars
        self.ROW_2 = "PFSCZZRLFCUOACDJMVMSPDFOIUYANDS"  # 31 chars
        self.ROW_3 = "OHCNSCDTGEUAAIYREBRTAWXVUIENLNN"  # 31 chars

        # Build keystream
        self.xor_keystream = self.ROW_1 + self.ROW_2 + self.ROW_3
        assert len(self.xor_keystream) == 93

        # Mask key
        self.mask_key = "CIAX"

    def alph26_to_alph25(self, text26):
        """Convert ALPH26 to ALPH25 (J->I)"""
        result = []
        for char in text26:
            if char == 'J':
                result.append('I')
            elif char in ALPH25:
                result.append(char)
            else:
                result.append('?')
        return ''.join(result)

    def decrypt(self, ciphertext):
        """Decrypt using tolerant XOR"""
        # Remove OBKR
        if ciphertext.startswith("OBKR"):
            ct_body = ciphertext[4:]
        else:
            ct_body = ciphertext

        # XOR decrypt (tolerant of 27-31)
        masked_26 = xor5_decrypt_string_tolerant(ct_body, self.xor_keystream)

        # Convert to ALPH25
        masked_25 = self.alph26_to_alph25(masked_26)

        # Base-5 unmask
        plaintext = base5_unmask_string(masked_25, self.mask_key)

        return plaintext

    def test(self):
        """Test with K4"""
        k4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

        print("K4 TOLERANT TEST")
        print("=" * 60)
        print(f"Using panel rows from K1-K3 segments")
        print(f"Row 1: {self.ROW_1}")
        print(f"Row 2: {self.ROW_2}")
        print(f"Row 3: {self.ROW_3}")
        print(f"Mask key: {self.mask_key}")

        pt = self.decrypt(k4)
        print(f"\nDecrypted: {pt}")
        print(f"Length: {len(pt)}")

        # Check anchors
        print(f"\nAt 63-69: {pt[63:69] if len(pt) > 69 else 'SHORT'}")
        print(f"Expected: BERLIN")
        print(f"At 69-74: {pt[69:74] if len(pt) > 74 else 'SHORT'}")
        print(f"Expected: CLOCK")

        has_berlin = len(pt) > 69 and "BERLIN" in pt[63:69]
        has_clock = len(pt) > 74 and "CLOCK" in pt[69:74]

        if has_berlin:
            print("✓ BERLIN found!")
        if has_clock:
            print("✓ CLOCK found!")

        # Check if BERLIN/CLOCK appear anywhere
        if "BERLIN" in pt:
            idx = pt.index("BERLIN")
            print(f"\nBERLIN found at position {idx}")
        if "CLOCK" in pt:
            idx = pt.index("CLOCK")
            print(f"CLOCK found at position {idx}")

        return has_berlin and has_clock


if __name__ == "__main__":
    cipher = K4Tolerant()
    success = cipher.test()
    print("\n" + "=" * 60)
    print(f"Result: {'✓ SUCCESS' if success else '✗ FAILURE'}")