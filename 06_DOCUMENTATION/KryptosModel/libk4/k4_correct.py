#!/usr/bin/env python3
"""
K4 Two-Layer Cryptosystem - Corrected Implementation
Using proper panel rows, per-letter pass-through, and drop-J alphabet
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from alphabets_fixed import ALPH25, ALPH26, c2i25
from mask_base5_fixed import base5_mask_string, base5_unmask_string
from xor5_fixed import xor5_encrypt_string, xor5_decrypt_string


class K4Correct:
    """
    Corrected K4 cipher implementation with:
    1. Proper panel row keys (from KRYPTOS tableau)
    2. Per-letter pass-through (when XOR result = 0)
    3. Drop-J alphabet (keeping X for CIAX key)
    """

    def __init__(self):
        # Correct panel rows from KRYPTOS tableau (31 chars each)
        self.ROW_X = "XWXZKRYPTOSABCDEFGHIJLMNQUVWXZK"      # Row 1, forward (31 chars)
        self.ROW_V = "VWXZKRYPTOSABCDEFGHIJLMNQUVWXZK"      # Row 2, REVERSED (31 chars, removed RY)
        self.ROW_T = "TNQUVWXZKRYPTOSABCDEFGHIJLMNQUV"      # Row 3, forward (31 chars)

        # Build 93-char XOR keystream
        self.xor_keystream = self.ROW_X + self.ROW_V[::-1] + self.ROW_T
        assert len(self.xor_keystream) == 93, f"XOR keystream wrong length: {len(self.xor_keystream)}"

        # Mask key (now valid in drop-J alphabet)
        self.mask_key = "CIAX"

    def alph25_to_alph26(self, text25):
        """
        Convert ALPH25 text to ALPH26 for XOR layer
        J's are never in ALPH25 text, so we can use direct mapping
        """
        result = []
        for char in text25:
            if char in ALPH25:
                # Direct mapping works since ALPH25 is subset of ALPH26
                result.append(char)
            else:
                result.append('?')
        return ''.join(result)

    def alph26_to_alph25(self, text26):
        """
        Convert ALPH26 text to ALPH25 after XOR layer
        J's become I's (standard practice)
        """
        result = []
        for char in text26:
            if char == 'J':
                result.append('I')  # J -> I mapping
            elif char in ALPH25:
                result.append(char)
            else:
                result.append('?')
        return ''.join(result)

    def encrypt(self, plaintext):
        """
        Encrypt plaintext using two-layer system

        Flow: PT (ALPH25) -> Base5 Mask -> XOR -> CT (ALPH26)
        """
        # Ensure plaintext is in ALPH25
        pt_clean = ''.join(c.upper() for c in plaintext if c.upper() in ALPH25)
        assert len(pt_clean) == 93, f"Plaintext must be 93 chars, got {len(pt_clean)}"

        # Layer A: Base-5 mask (in ALPH25 space)
        masked = base5_mask_string(pt_clean, self.mask_key)

        # Convert to ALPH26 for XOR layer
        masked_26 = self.alph25_to_alph26(masked)

        # Layer B: XOR with pass-through (in ALPH26 space)
        ct_body = xor5_encrypt_string(masked_26, self.xor_keystream)

        # Prepend OBKR header
        return "OBKR" + ct_body

    def decrypt(self, ciphertext):
        """
        Decrypt ciphertext using two-layer system

        Flow: CT (ALPH26) -> XOR inverse -> Base5 unmask -> PT (ALPH25)
        """
        # Remove OBKR header
        if ciphertext.startswith("OBKR"):
            ct_body = ciphertext[4:]
        else:
            ct_body = ciphertext

        assert len(ct_body) == 93, f"CT body must be 93 chars, got {len(ct_body)}"

        # Layer B inverse: XOR with pass-through (in ALPH26 space)
        masked_26 = xor5_decrypt_string(ct_body, self.xor_keystream)

        # Convert to ALPH25 for base-5 unmask
        masked_25 = self.alph26_to_alph25(masked_26)

        # Layer A inverse: Base-5 unmask (in ALPH25 space)
        plaintext = base5_unmask_string(masked_25, self.mask_key)

        return plaintext

    def verify(self):
        """Test with known K4 ciphertext"""
        k4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

        print("K4 CORRECTED IMPLEMENTATION TEST")
        print("=" * 60)
        print(f"Mask key: {self.mask_key} (valid in drop-J alphabet)")
        print(f"XOR keystream length: {len(self.xor_keystream)}")
        print(f"  Row X (fwd): {self.ROW_X}")
        print(f"  Row V (rev): {self.ROW_V[::-1]}")
        print(f"  Row T (fwd): {self.ROW_T}")

        print(f"\nK4 CT: {k4}")

        try:
            pt = self.decrypt(k4)
            print(f"\nDecrypted: {pt}")
            print(f"Length: {len(pt)}")

            # Check anchors
            print(f"\nAnchor check:")
            print(f"  At 63-69: {pt[63:69] if len(pt) > 69 else 'TOO SHORT'}")
            print(f"  Expected: BERLIN")
            print(f"  At 69-74: {pt[69:74] if len(pt) > 74 else 'TOO SHORT'}")
            print(f"  Expected: CLOCK")

            has_berlin = len(pt) > 69 and "BERLIN" in pt[63:69]
            has_clock = len(pt) > 74 and "CLOCK" in pt[69:74]

            if has_berlin:
                print("✓ BERLIN found at correct position!")
            if has_clock:
                print("✓ CLOCK found at correct position!")

            # Round-trip test
            print("\nRound-trip test:")
            re_enc = self.encrypt(pt)
            matches = re_enc == k4
            print(f"  Re-encrypted matches: {'✓ YES' if matches else '✗ NO'}")

            if not matches:
                # Find first difference
                for i in range(min(len(k4), len(re_enc))):
                    if k4[i] != re_enc[i]:
                        print(f"  First diff at position {i}:")
                        print(f"    Original: ...{k4[max(0,i-5):i+6]}...")
                        print(f"    Re-enc:   ...{re_enc[max(0,i-5):i+6]}...")
                        break

            return has_berlin and has_clock and matches

        except Exception as e:
            print(f"\nError during decryption: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    cipher = K4Correct()
    success = cipher.verify()
    print("\n" + "=" * 60)
    print(f"OVERALL: {'✓ SUCCESS' if success else '✗ FAILURE'}")
    print("=" * 60)