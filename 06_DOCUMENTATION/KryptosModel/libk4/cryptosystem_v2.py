"""
K4 two-layer cryptosystem implementation V2
Revised to properly handle 25/26 letter alphabet conversions
"""

from .alphabets import c2i25, i2c25, c2i26, i2c26, ALPH25, ALPH26


class K4CipherV2:
    """
    K4 two-layer cipher with proper alphabet handling

    System:
    - Plaintext (25-letter) → Layer A (base-5) → Layer B (XOR) → Ciphertext (26-letter)
    - Layer A: Base-5 masking in 25-letter space
    - Layer B: 5-bit XOR with pass-through rule
    """

    def __init__(self, mask_key="CIAX", xor_keys=None):
        """Initialize with keys"""
        self.mask_key = mask_key

        # Panel row keys (31 chars each)
        if xor_keys is None:
            self.xor_keys = [
                "VFPJUDEEHZWETZYVGWHKKQETGFQJNCE",
                "PFSCZZRLFCUOACDJMVMSPDFOIUYANDS",
                "OHCNSCDTGEUAAIYREBRTAWXVUIENLNN"
            ]
        else:
            self.xor_keys = xor_keys

    def encrypt(self, plaintext):
        """
        Encrypt plaintext (25-letter alphabet) to ciphertext (26-letter alphabet)
        """
        # Remove any X's and ensure uppercase
        pt_clean = ''.join(c for c in plaintext.upper() if c in ALPH25)

        # Layer A: Base-5 mask in 25-letter space
        pt_vals = [c2i25(c) for c in pt_clean]
        key_vals = [c2i25(c) for c in self.mask_key if c in ALPH25]

        masked = []
        for i, pt_val in enumerate(pt_vals):
            key_val = key_vals[i % len(key_vals)]
            # Simple modular addition in 25-letter space
            masked_val = (pt_val + key_val) % 25
            masked.append(masked_val)

        # Layer B: 5-bit XOR with pass-through
        # Build XOR key stream
        xor_stream = []
        for i in range(len(masked)):
            row = i // 31
            col = i % 31
            if row < len(self.xor_keys) and col < len(self.xor_keys[row]):
                xor_stream.append(c2i26(self.xor_keys[row][col]))
            else:
                xor_stream.append(0)

        # Apply XOR with pass-through rule
        ct_vals = []
        for i, masked_val in enumerate(masked):
            xor_val = xor_stream[i]

            # Perform bitwise XOR with pass-through
            result = 0
            for bit in range(5):
                masked_bit = (masked_val >> bit) & 1
                xor_bit = (xor_val >> bit) & 1

                # Pass-through: if XOR bit is 0, use masked bit unchanged
                if xor_bit == 0:
                    result_bit = masked_bit
                else:
                    result_bit = masked_bit ^ xor_bit

                result |= (result_bit << bit)

            ct_vals.append(result)

        # Convert to 26-letter alphabet ciphertext
        ciphertext = ''.join(i2c26(v) for v in ct_vals)

        # Add OBKR header
        return "OBKR" + ciphertext

    def decrypt(self, ciphertext):
        """
        Decrypt ciphertext (26-letter alphabet) to plaintext (25-letter alphabet)
        """
        # Remove OBKR header if present
        if ciphertext.startswith("OBKR"):
            ct_body = ciphertext[4:]
        else:
            ct_body = ciphertext

        # Convert from 26-letter alphabet
        ct_vals = [c2i26(c) for c in ct_body if c in ALPH26]

        # Build XOR key stream
        xor_stream = []
        for i in range(len(ct_vals)):
            row = i // 31
            col = i % 31
            if row < len(self.xor_keys) and col < len(self.xor_keys[row]):
                xor_stream.append(c2i26(self.xor_keys[row][col]))
            else:
                xor_stream.append(0)

        # Layer B inverse: XOR with pass-through (self-inverse)
        masked = []
        for i, ct_val in enumerate(ct_vals):
            xor_val = xor_stream[i]

            # XOR with pass-through is self-inverse
            result = 0
            for bit in range(5):
                ct_bit = (ct_val >> bit) & 1
                xor_bit = (xor_val >> bit) & 1

                if xor_bit == 0:
                    result_bit = ct_bit
                else:
                    result_bit = ct_bit ^ xor_bit

                result |= (result_bit << bit)

            # Map to 25-letter range
            masked.append(result % 25)

        # Layer A inverse: Base-5 unmask in 25-letter space
        key_vals = [c2i25(c) for c in self.mask_key if c in ALPH25]

        plaintext = []
        for i, masked_val in enumerate(masked):
            key_val = key_vals[i % len(key_vals)]
            # Simple modular subtraction in 25-letter space
            pt_val = (masked_val - key_val) % 25
            plaintext.append(i2c25(pt_val))

        return ''.join(plaintext)

    def verify(self):
        """Test with known K4 ciphertext"""
        k4_ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

        pt = self.decrypt(k4_ct)
        print(f"Decrypted: {pt}")
        print(f"Length: {len(pt)}")

        # Check for anchors
        has_berlin = "BERLIN" in pt[63:69]
        has_clock = "CLOCK" in pt[69:74]

        print(f"BERLIN at 63-69: {'✓' if has_berlin else '✗'} (found: {pt[63:69]})")
        print(f"CLOCK at 69-74: {'✓' if has_clock else '✗'} (found: {pt[69:74]})")

        # Round-trip test
        re_encrypted = self.encrypt(pt)
        matches = re_encrypted == k4_ct

        print(f"Round-trip: {'✓' if matches else '✗'}")
        if not matches:
            # Show where they differ
            for i in range(min(len(k4_ct), len(re_encrypted))):
                if i >= len(k4_ct) or i >= len(re_encrypted) or k4_ct[i] != re_encrypted[i]:
                    print(f"  First diff at position {i}: '{k4_ct[i]}' vs '{re_encrypted[i]}'")
                    break

        return has_berlin and has_clock and matches