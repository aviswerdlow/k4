#!/usr/bin/env python3
"""
K4 Two-Layer Cryptosystem - Final Implementation
Handles 25/26 letter alphabet conversion properly
"""


class K4Final:
    """
    K4 two-layer cipher final implementation
    Layer A: Base-5 mask (25-letter alphabet)
    Layer B: 5-bit XOR with pass-through (26-letter values)
    """

    def __init__(self):
        # 25-letter alphabet (no X)
        self.alph25 = "ABCDEFGHIJKLMNOPQRSTUVWYZ"
        self.c2i25 = {c: i for i, c in enumerate(self.alph25)}
        self.i2c25 = {i: c for i, c in enumerate(self.alph25)}

        # 26-letter alphabet
        self.alph26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.c2i26 = {c: i for i, c in enumerate(self.alph26)}
        self.i2c26 = {i: c for i, c in enumerate(self.alph26)}

        # Mask key (using W instead of X for 25-letter alphabet)
        self.mask_key = "CIAW"  # Changed from CIAX

        # Panel row keys (31 chars each)
        self.xor_keys = [
            "VFPJUDEEHZWETZYVGWHKKQETGFQJNCE",  # Row 1
            "PFSCZZRLFCUOACDJMVMSPDFOIUYANDS",  # Row 2
            "OHCNSCDTGEUAAIYREBRTAWXVUIENLNN"   # Row 3
        ]

    def encrypt(self, plaintext):
        """Encrypt plaintext to ciphertext"""
        # Ensure plaintext is in 25-letter alphabet
        pt_clean = ''.join(c.upper() for c in plaintext if c.upper() in self.alph25)

        # Layer A: Base-5 mask
        pt_vals = [self.c2i25[c] for c in pt_clean]
        mask_vals = [self.c2i25[c] for c in self.mask_key]

        masked = []
        for i, pt_val in enumerate(pt_vals):
            mask_val = mask_vals[i % len(mask_vals)]
            # Simple modular addition
            masked.append((pt_val + mask_val) % 25)

        # Convert masked values to 26-letter for XOR
        # Map 25-letter to 26-letter by shifting values >= 23 up by 1 (skip X)
        masked_26 = []
        for val in masked:
            if val < 23:  # A-W (positions 0-22)
                masked_26.append(val)
            else:  # Y-Z (positions 23-24 in 25-letter → 24-25 in 26-letter)
                masked_26.append(val + 1)

        # Layer B: XOR with pass-through
        ct_vals = []
        for i, val in enumerate(masked_26):
            # Get XOR key value
            row = i // 31
            col = i % 31
            if row < len(self.xor_keys) and col < len(self.xor_keys[row]):
                xor_val = self.c2i26[self.xor_keys[row][col]]
            else:
                xor_val = 0

            # Apply XOR with pass-through
            result = 0
            for bit in range(5):
                val_bit = (val >> bit) & 1
                xor_bit = (xor_val >> bit) & 1

                if xor_bit == 0:
                    result_bit = val_bit  # Pass through
                else:
                    result_bit = val_bit ^ xor_bit  # XOR

                result |= (result_bit << bit)

            ct_vals.append(result % 26)  # Ensure in 26-letter range

        # Convert to ciphertext
        ciphertext = ''.join(self.i2c26[v] for v in ct_vals)
        return "OBKR" + ciphertext

    def decrypt(self, ciphertext):
        """Decrypt ciphertext to plaintext"""
        # Remove OBKR header
        if ciphertext.startswith("OBKR"):
            ct_body = ciphertext[4:]
        else:
            ct_body = ciphertext

        # Convert to values
        ct_vals = [self.c2i26[c] for c in ct_body if c in self.alph26]

        # Layer B inverse: XOR with pass-through (self-inverse)
        masked_26 = []
        for i, ct_val in enumerate(ct_vals):
            # Get XOR key value
            row = i // 31
            col = i % 31
            if row < len(self.xor_keys) and col < len(self.xor_keys[row]):
                xor_val = self.c2i26[self.xor_keys[row][col]]
            else:
                xor_val = 0

            # Apply XOR inverse (same operation)
            result = 0
            for bit in range(5):
                ct_bit = (ct_val >> bit) & 1
                xor_bit = (xor_val >> bit) & 1

                if xor_bit == 0:
                    result_bit = ct_bit  # Pass through
                else:
                    result_bit = ct_bit ^ xor_bit  # XOR

                result |= (result_bit << bit)

            masked_26.append(result)

        # Convert from 26-letter to 25-letter
        # Map values 24-25 (Y-Z in 26-letter) to 23-24 (Y-Z in 25-letter)
        masked = []
        for val in masked_26:
            if val < 23:  # A-W
                masked.append(val % 25)
            elif val == 23:  # X in 26-letter - shouldn't happen in valid CT
                masked.append(22)  # Map to W
            else:  # Y-Z (24-25 in 26-letter)
                masked.append((val - 1) % 25)

        # Layer A inverse: Unmask
        mask_vals = [self.c2i25[c] for c in self.mask_key]

        plaintext = []
        for i, masked_val in enumerate(masked):
            mask_val = mask_vals[i % len(mask_vals)]
            # Simple modular subtraction
            pt_val = (masked_val - mask_val) % 25
            plaintext.append(self.i2c25[pt_val])

        return ''.join(plaintext)

    def test(self):
        """Test with K4 ciphertext"""
        k4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

        print("K4 FINAL TEST")
        print("=" * 60)
        print(f"Mask key: {self.mask_key}")
        print(f"K4 CT: {k4}")

        pt = self.decrypt(k4)
        print(f"\nDecrypted: {pt}")
        print(f"Length: {len(pt)}")

        # Check anchors
        print(f"\nAt 63-69: {pt[63:69]} (expect BERLIN)")
        print(f"At 69-74: {pt[69:74]} (expect CLOCK)")

        has_berlin = "BERLIN" in pt[63:69]
        has_clock = "CLOCK" in pt[69:74]

        if has_berlin:
            print("✓ BERLIN found!")
        if has_clock:
            print("✓ CLOCK found!")

        # Round-trip
        re_enc = self.encrypt(pt)
        matches = re_enc == k4
        print(f"\nRound-trip: {'✓ PASS' if matches else '✗ FAIL'}")

        if not matches:
            # Find first difference
            for i in range(min(len(k4), len(re_enc))):
                if k4[i] != re_enc[i]:
                    print(f"First diff at {i}: '{k4[i]}' vs '{re_enc[i]}'")
                    print(f"Context: ...{k4[max(0,i-5):i+6]}...")
                    print(f"         ...{re_enc[max(0,i-5):i+6]}...")
                    break

        return has_berlin and has_clock and matches


if __name__ == "__main__":
    cipher = K4Final()
    success = cipher.test()