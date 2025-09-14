"""
Hörenberg's EXACT 5-bit XOR implementation based on reverse engineering.

Key finding: When r=C⊕K is in range 27-31, Hörenberg outputs C (like pass-through)
This is different from cyclic mapping.
"""


def letter_to_code5(letter):
    """
    Convert letter to 5-bit code (A=1, B=2, ..., Z=26)
    """
    if not letter.isalpha():
        return -1
    return ord(letter.upper()) - ord('A') + 1


def code5_to_letter(code):
    """
    Convert 5-bit code back to letter
    """
    if 1 <= code <= 26:
        return chr(ord('A') + code - 1)
    return '?'


def xor5_hoerenberg(ct_letter, key_letter):
    """
    Apply Hörenberg's exact 5-bit XOR convention.

    Based on reverse engineering his published strings:
    - If r = C⊕K = 0: output C (pass-through)
    - If r ∈ {1..26}: output letter(r)
    - If r ∈ {27..31}: output C (treat like pass-through!)

    This explains why positions with R27-31 show the cipher letter in P.
    """
    ct_code = letter_to_code5(ct_letter)
    key_code = letter_to_code5(key_letter)

    if ct_code == -1 or key_code == -1:
        return '?'

    # 5-bit XOR
    r = ct_code ^ key_code

    if r == 0:
        # Standard pass-through
        return ct_letter
    elif 1 <= r <= 26:
        # Valid letter range
        return code5_to_letter(r)
    else:
        # r in 27-31: Hörenberg treats these as pass-through!
        return ct_letter


def xor5_string_hoerenberg(ciphertext, keystream):
    """
    Apply Hörenberg's XOR to entire strings.
    """
    if len(ciphertext) != len(keystream):
        raise ValueError(f"Length mismatch: CT={len(ciphertext)}, Key={len(keystream)}")

    result = []
    for ct_char, key_char in zip(ciphertext, keystream):
        p_char = xor5_hoerenberg(ct_char, key_char)
        result.append(p_char)

    return ''.join(result)