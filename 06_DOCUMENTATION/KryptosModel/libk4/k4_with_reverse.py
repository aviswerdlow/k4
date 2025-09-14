#!/usr/bin/env python3
"""
K4 Implementation with REQUIRED reverse steps and programmatic tableau rows
This version includes both missing pieces from the specification
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from alphabets_fixed import ALPH25, ALPH26
from mask_base5_fixed import base5_mask_string, base5_unmask_string
from xor5_fixed import xor5_encrypt_string, xor5_decrypt_string
from tableau_builder import build_xor_keystream, display_rows


class K4WithReverse:
    """
    Complete K4 implementation with:
    1. Reverse step before/after XOR layer
    2. Programmatically built tableau rows
    3. Drop-J alphabet with CIAX key
    4. Per-letter pass-through (XOR result = 0)
    """

    def __init__(self, reverse_v=True, phase=0):
        """
        Initialize with tableau-based keystream

        Args:
            reverse_v: Whether to reverse the V row (default: True)
            phase: Phase offset for keystream (0-92)
        """
        # Build keystream programmatically
        self.xor_keystream = build_xor_keystream(reverse_v=reverse_v, phase=phase)
        self.reverse_v = reverse_v
        self.phase = phase

        # Mask key (valid in drop-J alphabet)
        self.mask_key = "CIAX"

    def alph25_to_alph26(self, text25):
        """Convert ALPH25 to ALPH26 for XOR layer"""
        result = []
        for char in text25:
            if char in ALPH25:
                result.append(char)
            else:
                result.append('?')
        return ''.join(result)

    def alph26_to_alph25(self, text26):
        """Convert ALPH26 to ALPH25 after XOR layer (J->I)"""
        result = []
        for char in text26:
            if char == 'J':
                result.append('I')
            elif char in ALPH25:
                result.append(char)
            else:
                result.append('?')
        return ''.join(result)

    def encrypt(self, plaintext):
        """
        Encrypt with complete two-layer system including reverse

        Flow: PT → Base5 Mask → XOR → REVERSE → CT
        """
        # Clean plaintext to ALPH25
        pt_clean = ''.join(c.upper() for c in plaintext if c.upper() in ALPH25)
        assert len(pt_clean) == 93, f"Plaintext must be 93 chars, got {len(pt_clean)}"

        # Layer A: Base-5 mask (in ALPH25 space)
        masked = base5_mask_string(pt_clean, self.mask_key)

        # Convert to ALPH26 for XOR
        masked_26 = self.alph25_to_alph26(masked)

        # Layer B: XOR with pass-through
        ct_body_rev = xor5_encrypt_string(masked_26, self.xor_keystream)

        # CRITICAL: Reverse the 93-char body after XOR
        ct_body = ct_body_rev[::-1]

        # Prepend OBKR header
        return "OBKR" + ct_body

    def decrypt(self, ciphertext):
        """
        Decrypt with complete two-layer system including reverse

        Flow: CT → REVERSE → XOR inverse → Base5 unmask → PT
        """
        # Remove OBKR header
        if ciphertext.startswith("OBKR"):
            ct_body = ciphertext[4:]
        else:
            ct_body = ciphertext

        assert len(ct_body) == 93, f"CT body must be 93 chars, got {len(ct_body)}"

        # CRITICAL: Reverse the 93-char body before XOR
        ct_rev = ct_body[::-1]

        # Layer B inverse: XOR with pass-through
        masked_26 = xor5_decrypt_string(ct_rev, self.xor_keystream)

        # Convert to ALPH25
        masked_25 = self.alph26_to_alph25(masked_26)

        # Layer A inverse: Base-5 unmask
        plaintext = base5_unmask_string(masked_25, self.mask_key)

        return plaintext

    def verify(self):
        """Test with K4 ciphertext"""
        k4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

        print("K4 WITH REVERSE STEPS")
        print("=" * 60)
        print(f"Configuration:")
        print(f"  Mask key: {self.mask_key}")
        print(f"  V reversed: {self.reverse_v}")
        print(f"  Phase: {self.phase}")
        print(f"  Keystream (first 31): {self.xor_keystream[:31]}")

        try:
            # Decrypt
            pt = self.decrypt(k4)
            print(f"\nDecrypted: {pt}")
            print(f"Length: {len(pt)}")

            # Check anchors
            print(f"\nAnchor check:")
            if len(pt) >= 74:
                print(f"  At 63-69: {pt[63:69]} (expect BERLIN)")
                print(f"  At 69-74: {pt[69:74]} (expect CLOCK)")

                has_berlin = "BERLIN" in pt[63:69]
                has_clock = "CLOCK" in pt[69:74]

                if has_berlin:
                    print("  ✓ BERLIN found!")
                if has_clock:
                    print("  ✓ CLOCK found!")
            else:
                has_berlin = has_clock = False
                print("  Plaintext too short!")

            # Round-trip test
            print("\nRound-trip test:")
            re_enc = self.encrypt(pt)
            matches = re_enc == k4
            print(f"  Matches: {'✓ YES' if matches else '✗ NO'}")

            if not matches:
                # Find first difference
                for i in range(min(len(k4), len(re_enc))):
                    if k4[i] != re_enc[i]:
                        print(f"  First diff at position {i}:")
                        print(f"    Original: ...{k4[max(0,i-5):i+6]}...")
                        print(f"    Re-enc:   ...{re_enc[max(0,i-5):i+6]}...")
                        break

            return has_berlin and has_clock and matches

        except ValueError as e:
            print(f"\nError: {e}")
            return False


def test_configurations():
    """Test different configurations to find working parameters"""
    print("\nTesting configurations with reverse step...")
    print("=" * 60)

    configs = [
        (True, 0, "V reversed, phase 0"),
        (False, 0, "V forward, phase 0"),
        (True, 1, "V reversed, phase 1"),
        (True, 31, "V reversed, phase 31"),
    ]

    for reverse_v, phase, desc in configs:
        print(f"\nTesting: {desc}")
        cipher = K4WithReverse(reverse_v=reverse_v, phase=phase)
        try:
            success = cipher.verify()
            if success:
                print(f"\n✓✓✓ SUCCESS with {desc}!")
                return True
        except Exception as e:
            print(f"  Failed: {e}")

    return False


if __name__ == "__main__":
    # Display tableau rows
    display_rows()

    # Test with reverse steps included
    print("\n" + "=" * 60)
    print("MAIN TEST WITH REVERSE STEPS")
    print("=" * 60)

    # Try default configuration first
    cipher = K4WithReverse()
    success = cipher.verify()

    if not success:
        # Try other configurations
        print("\n" + "=" * 60)
        print("TRYING ALTERNATIVE CONFIGURATIONS")
        print("=" * 60)
        success = test_configurations()

    print("\n" + "=" * 60)
    print(f"FINAL RESULT: {'✓ SUCCESS' if success else '✗ FAILURE'}")
    print("=" * 60)