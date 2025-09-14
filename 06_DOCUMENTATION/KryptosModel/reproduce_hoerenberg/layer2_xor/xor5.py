"""
5-bit XOR implementation matching Hörenberg's approach
Maps A..Z to 1..26 and applies XOR with pass-through rule
"""


def letter_to_code5(letter):
    """
    Convert letter to 5-bit code (A=1, B=2, ..., Z=26)

    Args:
        letter: Single character A-Z

    Returns:
        Integer 1-26, or -1 if invalid
    """
    if not letter.isalpha():
        return -1
    return ord(letter.upper()) - ord('A') + 1


def code5_to_letter(code):
    """
    Convert 5-bit code back to letter

    Args:
        code: Integer 1-26

    Returns:
        Letter A-Z, or '?' if invalid
    """
    if 1 <= code <= 26:
        return chr(ord('A') + code - 1)
    return '?'


def xor5_with_passthrough(ct_letter, key_letter):
    """
    Apply 5-bit XOR with Hörenberg's pass-through rule

    If XOR result is 0, output the CT letter (pass-through).
    If result is 1-26, map back to letter.
    If result is 27-31, still output (marked as invalid in analysis).

    Args:
        ct_letter: Ciphertext letter
        key_letter: Key letter

    Returns:
        Result letter or pass-through
    """
    ct_code = letter_to_code5(ct_letter)
    key_code = letter_to_code5(key_letter)

    if ct_code == -1 or key_code == -1:
        return '?'

    # 5-bit XOR
    result = ct_code ^ key_code

    if result == 0:
        # Pass-through rule (Rockex discriminator)
        return ct_letter
    elif 1 <= result <= 26:
        # Valid letter range
        return code5_to_letter(result)
    else:
        # Result is 27-31 - Hörenberg appears to map these cyclically
        # 27 -> A, 28 -> B, 29 -> C, 30 -> D, 31 -> E
        # Or he might skip them entirely for IoC calculation
        # Looking at his P string, these positions seem to be regular letters
        # Let's map them modulo 26
        return code5_to_letter((result - 1) % 26 + 1)


def xor5_string(ciphertext, keystream):
    """
    Apply XOR with pass-through to entire strings

    Args:
        ciphertext: CT string
        keystream: Key string (must be same length)

    Returns:
        P (plaintext) string after XOR
    """
    if len(ciphertext) != len(keystream):
        raise ValueError(f"Length mismatch: CT={len(ciphertext)}, Key={len(keystream)}")

    result = []
    for ct_char, key_char in zip(ciphertext, keystream):
        result.append(xor5_with_passthrough(ct_char, key_char))

    return ''.join(result)


def test_xor():
    """Test XOR operations to verify implementation"""
    print("Testing 5-bit XOR with pass-through:")
    print("=" * 40)

    # Test cases
    tests = [
        ('A', 'A', 'A'),  # 1 XOR 1 = 0 -> pass-through
        ('B', 'C', 'A'),  # 2 XOR 3 = 1 -> A
        ('Z', 'Y', 'C'),  # 26 XOR 25 = 3 -> C
    ]

    for ct, key, expected in tests:
        result = xor5_with_passthrough(ct, key)
        print(f"{ct} XOR {key} = {result} (expected {expected})")

    # Test a string from Hörenberg's example
    print("\nTesting string XOR:")
    ct_sample = "UOXO"
    key_sample = "FGHI"
    p_sample = xor5_string(ct_sample, key_sample)
    print(f"CT:  {ct_sample}")
    print(f"Key: {key_sample}")
    print(f"P:   {p_sample}")


if __name__ == "__main__":
    test_xor()