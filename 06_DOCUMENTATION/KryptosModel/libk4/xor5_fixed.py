"""
Fixed 5-bit XOR layer with per-letter pass-through rule
Pass-through occurs when XOR result equals 0 (not when key bit is 0)
"""

from alphabets_fixed import code5_A1Z26, from_1_26


def xor5_letter(ct_letter, key_letter):
    """
    XOR two letters in A..Z space (1..26 coding)

    Returns:
        XOR result (0..31)
    """
    rc = code5_A1Z26(ct_letter)
    rk = code5_A1Z26(key_letter)

    if rc == -1 or rk == -1:
        return -1

    return rc ^ rk


def xor5_decrypt_letter(ct_letter, key_letter):
    """
    Decrypt a single letter using XOR with pass-through

    Pass-through rule: If XOR result is 0, pass ct_letter unchanged
    """
    r = xor5_letter(ct_letter, key_letter)

    if r == -1:
        return '?'
    elif r == 0:
        # Per-letter pass-through (Rockex-style zero)
        return ct_letter
    elif 1 <= r <= 26:
        return from_1_26(r)
    else:
        # r in {27..31} indicates wrong row/orientation
        raise ValueError(f"Invalid XOR result {r} (27..31 range) - check panel row keys")


def xor5_encrypt_letter(pt_letter, key_letter):
    """
    Encrypt a single letter using XOR with pass-through

    Note: For standard XOR, encryption and decryption are the same operation
    """
    return xor5_decrypt_letter(pt_letter, key_letter)


def xor5_decrypt_string(ciphertext, keystream):
    """
    Decrypt entire string using XOR with pass-through

    Args:
        ciphertext: String of A..Z letters
        keystream: String of A..Z key letters (same length)

    Returns:
        Decrypted string
    """
    if len(ciphertext) != len(keystream):
        raise ValueError(f"Length mismatch: CT={len(ciphertext)}, Key={len(keystream)}")

    result = []
    for ct_char, key_char in zip(ciphertext, keystream):
        result.append(xor5_decrypt_letter(ct_char, key_char))

    return ''.join(result)


def xor5_encrypt_string(plaintext, keystream):
    """
    Encrypt entire string using XOR with pass-through
    """
    return xor5_decrypt_string(plaintext, keystream)