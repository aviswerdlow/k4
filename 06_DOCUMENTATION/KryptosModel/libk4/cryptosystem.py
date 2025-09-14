"""
K4 two-layer cryptosystem implementation
Combines XOR layer (Layer B) and base-5 mask layer (Layer A)
"""

from .alphabets import encode5, decode5, c2i26, i2c26, ALPH26
from .mask_base5 import base5_mask, base5_unmask
from .xor5 import xor5_passthrough, xor5_passthrough_decrypt


class K4Cipher:
    """
    K4 two-layer cipher implementation

    The system works as:
    1. Plaintext → Layer A (base-5 mask) → Layer B (XOR) → Ciphertext
    2. Ciphertext → Layer B inverse → Layer A inverse → Plaintext
    """

    def __init__(self, mask_key="CIAX", xor_keys=None):
        """
        Initialize K4 cipher with keys

        Args:
            mask_key: Key for base-5 masking layer (default: "CIAX")
            xor_keys: List of 3 keys for XOR layer (panel row keys)
                     If None, uses default Kryptos panel rows
        """
        self.mask_key = mask_key

        # Default XOR keys from Kryptos right panel rows
        if xor_keys is None:
            self.xor_keys = [
                "VFPJUDEEHZWETZYVGWHKKQETGFQJNCE",  # Row 1 (31 chars)
                "PFSCZZRLFCUOACDJMVMSPDFOIUYANDS",  # Row 2 (31 chars, removed extra P)
                "OHCNSCDTGEUAAIYREBRTAWXVUIENLNN"   # Row 3 (31 chars)
            ]
        else:
            self.xor_keys = xor_keys

    def _get_xor_key_for_position(self, pos):
        """Get the appropriate XOR key value for a given position"""
        # Each row handles 31 characters
        row = pos // 31
        col = pos % 31

        if row >= len(self.xor_keys):
            return 0  # No key for positions beyond our keys

        key_char = self.xor_keys[row][col] if col < len(self.xor_keys[row]) else 'A'
        return c2i26(key_char)

    def encrypt(self, plaintext):
        """
        Encrypt plaintext using two-layer system

        Args:
            plaintext: Input plaintext (93 characters expected)

        Returns:
            Ciphertext string with OBKR header prepended
        """
        # Layer A: Base-5 mask (operates on 25-letter alphabet)
        masked_values = base5_mask(plaintext, self.mask_key)

        # Layer B: XOR with pass-through (operates on 5-bit values)
        # Build XOR key stream for the message length
        xor_key_stream = []
        for i in range(len(masked_values)):
            xor_key_stream.append(self._get_xor_key_for_position(i))

        # Apply XOR layer
        ciphertext_values = xor5_passthrough(masked_values, xor_key_stream)

        # Convert to text (using 26-letter alphabet for output)
        ciphertext = decode5(ciphertext_values, alphabet='26')

        # Prepend OBKR header
        return "OBKR" + ciphertext

    def decrypt(self, ciphertext):
        """
        Decrypt ciphertext using two-layer system

        Args:
            ciphertext: Input ciphertext (should start with OBKR)

        Returns:
            Plaintext string
        """
        # Remove OBKR header if present
        if ciphertext.startswith("OBKR"):
            ciphertext = ciphertext[4:]

        # Convert to 5-bit values
        ct_values = encode5(ciphertext, alphabet='26')

        # Build XOR key stream for the message length
        xor_key_stream = []
        for i in range(len(ct_values)):
            xor_key_stream.append(self._get_xor_key_for_position(i))

        # Layer B inverse: XOR with pass-through (self-inverse)
        masked_values = xor5_passthrough_decrypt(ct_values, xor_key_stream)

        # Ensure values are in 25-letter range for base-5 unmask
        masked_values = [v % 25 for v in masked_values]

        # Layer A inverse: Base-5 unmask
        plaintext = base5_unmask(masked_values, self.mask_key)

        return plaintext

    def verify_roundtrip(self, plaintext=None, expected_ct=None):
        """
        Verify that encryption and decryption round-trip correctly

        Args:
            plaintext: Optional plaintext to test
            expected_ct: Optional expected ciphertext (with OBKR header)

        Returns:
            Tuple of (success, details_dict)
        """
        # Use default K4 ciphertext if not provided
        if expected_ct is None:
            expected_ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

        # If plaintext provided, test encryption
        if plaintext is not None:
            encrypted = self.encrypt(plaintext)
            decrypted = self.decrypt(encrypted)

            return (
                encrypted == expected_ct and decrypted == plaintext,
                {
                    "plaintext": plaintext,
                    "encrypted": encrypted,
                    "expected_ct": expected_ct,
                    "match_ct": encrypted == expected_ct,
                    "decrypted": decrypted,
                    "match_pt": decrypted == plaintext
                }
            )

        # Otherwise, test decryption of known ciphertext
        decrypted = self.decrypt(expected_ct)
        re_encrypted = self.encrypt(decrypted)

        return (
            re_encrypted == expected_ct,
            {
                "ciphertext": expected_ct,
                "decrypted": decrypted,
                "re_encrypted": re_encrypted,
                "match": re_encrypted == expected_ct
            }
        )