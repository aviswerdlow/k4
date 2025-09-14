"""
XOR layer that handles 27-31 results by mapping them back to valid range
"""

from alphabets_fixed import code5_A1Z26, from_1_26


def xor5_decrypt_letter_tolerant(ct_letter, key_letter):
    """
    Decrypt with XOR, handling 27-31 by modulo 26

    When XOR gives 27-31, map back to 1-5
    """
    rc = code5_A1Z26(ct_letter)
    rk = code5_A1Z26(key_letter)

    if rc == -1 or rk == -1:
        return '?'

    r = rc ^ rk

    if r == 0:
        # Pass-through
        return ct_letter
    elif 1 <= r <= 26:
        return from_1_26(r)
    else:
        # Map 27-31 to 1-5 (or use modulo)
        r_mapped = ((r - 1) % 26) + 1
        return from_1_26(r_mapped)


def xor5_decrypt_string_tolerant(ciphertext, keystream):
    """Decrypt with tolerance for 27-31 results"""
    if len(ciphertext) != len(keystream):
        raise ValueError(f"Length mismatch: CT={len(ciphertext)}, Key={len(keystream)}")

    result = []
    for ct_char, key_char in zip(ciphertext, keystream):
        result.append(xor5_decrypt_letter_tolerant(ct_char, key_char))

    return ''.join(result)