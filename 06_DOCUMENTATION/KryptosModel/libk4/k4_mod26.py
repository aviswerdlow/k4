#!/usr/bin/env python3
"""
K4 Implementation using mod-26 operations instead of 5-bit XOR
Tests both Vigenère and Beaufort with the same tableau rows
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from alphabets_fixed import ALPH25, ALPH26
from mask_base5_fixed import base5_mask_string, base5_unmask_string
from mod26_layer import (vigenere_encrypt_string, vigenere_decrypt_string,
                         beaufort_encrypt_string, beaufort_decrypt_string)
from tableau_builder import build_xor_keystream


class K4Mod26:
    """
    K4 with mod-26 operations replacing XOR
    Still uses:
    - Reverse before/after Layer B
    - Drop-J alphabet with CIAX
    - Tableau-based keystream
    """

    def __init__(self, cipher_type='vigenere', reverse_v=True, phase=0):
        """
        Initialize with mod-26 cipher

        Args:
            cipher_type: 'vigenere' or 'beaufort'
            reverse_v: Whether to reverse V row
            phase: Phase offset for keystream
        """
        self.cipher_type = cipher_type
        self.keystream = build_xor_keystream(reverse_v=reverse_v, phase=phase)
        self.reverse_v = reverse_v
        self.phase = phase
        self.mask_key = "CIAX"

        # Select cipher functions
        if cipher_type == 'vigenere':
            self.layer_b_encrypt = vigenere_encrypt_string
            self.layer_b_decrypt = vigenere_decrypt_string
        else:  # beaufort
            self.layer_b_encrypt = beaufort_encrypt_string
            self.layer_b_decrypt = beaufort_decrypt_string

    def alph25_to_alph26(self, text25):
        """Convert ALPH25 to ALPH26"""
        result = []
        for char in text25:
            if char in ALPH25:
                result.append(char)
            else:
                result.append('?')
        return ''.join(result)

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

    def encrypt(self, plaintext):
        """Encrypt using mod-26 operations"""
        # Clean to ALPH25
        pt_clean = ''.join(c.upper() for c in plaintext if c.upper() in ALPH25)
        assert len(pt_clean) == 93

        # Layer A: Base-5 mask
        masked = base5_mask_string(pt_clean, self.mask_key)

        # Convert to ALPH26
        masked_26 = self.alph25_to_alph26(masked)

        # Layer B: Mod-26 cipher
        ct_body_rev = self.layer_b_encrypt(masked_26, self.keystream)

        # REVERSE after Layer B
        ct_body = ct_body_rev[::-1]

        return "OBKR" + ct_body

    def decrypt(self, ciphertext):
        """Decrypt using mod-26 operations"""
        # Remove header
        if ciphertext.startswith("OBKR"):
            ct_body = ciphertext[4:]
        else:
            ct_body = ciphertext

        assert len(ct_body) == 93

        # REVERSE before Layer B
        ct_rev = ct_body[::-1]

        # Layer B inverse: Mod-26 cipher
        masked_26 = self.layer_b_decrypt(ct_rev, self.keystream)

        # Convert to ALPH25
        masked_25 = self.alph26_to_alph25(masked_26)

        # Layer A inverse: Base-5 unmask
        plaintext = base5_unmask_string(masked_25, self.mask_key)

        return plaintext

    def verify(self):
        """Test with K4"""
        k4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

        print(f"\nK4 {self.cipher_type.upper()} TEST")
        print("=" * 60)
        print(f"Config: {self.cipher_type}, V_rev={self.reverse_v}, phase={self.phase}")

        pt = self.decrypt(k4)
        print(f"Decrypted: {pt[:40]}...")

        # Check anchors
        has_berlin = len(pt) >= 69 and "BERLIN" in pt[63:69]
        has_clock = len(pt) >= 74 and "CLOCK" in pt[69:74]

        if has_berlin or has_clock:
            print(f"At 63-69: {pt[63:69]}")
            print(f"At 69-74: {pt[69:74]}")
            if has_berlin:
                print("✓ BERLIN found!")
            if has_clock:
                print("✓ CLOCK found!")

        # Round-trip
        re_enc = self.encrypt(pt)
        matches = re_enc == k4

        if matches:
            print("✓ Round-trip matches!")
        else:
            # Find difference
            for i in range(min(len(k4), len(re_enc))):
                if k4[i] != re_enc[i]:
                    print(f"✗ Round-trip fails at position {i}")
                    break

        return has_berlin and has_clock and matches


def search_mod26():
    """Search for working configuration with mod-26"""
    print("SEARCHING MOD-26 CONFIGURATIONS")
    print("=" * 60)

    best_results = []

    for cipher_type in ['vigenere', 'beaufort']:
        for reverse_v in [True, False]:
            for phase in [0, 1, 31, 79]:  # Test promising phases
                try:
                    cipher = K4Mod26(cipher_type=cipher_type,
                                   reverse_v=reverse_v,
                                   phase=phase)
                    success = cipher.verify()

                    if success:
                        print(f"\n✓✓✓ SUCCESS!")
                        print(f"Cipher: {cipher_type}")
                        print(f"V reversed: {reverse_v}")
                        print(f"Phase: {phase}")
                        return True

                except Exception as e:
                    print(f"  {cipher_type}, V_rev={reverse_v}, phase={phase}: Error - {e}")

    return False


if __name__ == "__main__":
    success = search_mod26()

    print("\n" + "=" * 60)
    if success:
        print("✓ FOUND WORKING CONFIGURATION WITH MOD-26!")
    else:
        print("✗ No mod-26 configuration produced correct results")
        print("\nConclusion: Either:")
        print("1. The tableau row construction method is wrong")
        print("2. The reverse step placement is wrong")
        print("3. The two-layer system interpretation is wrong")
        print("4. The key material (CIAX, panel rows) is wrong")