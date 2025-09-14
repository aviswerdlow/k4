"""
Mod-26 operations (Vigenère/Beaufort) as alternative to 5-bit XOR
Uses same tableau rows but with classical cipher operations
"""

from alphabets_fixed import code5_A1Z26, from_1_26


def vigenere_encrypt_letter(pt_letter, key_letter):
    """
    Vigenère encryption: CT = (PT + KEY) mod 26
    Using 1-26 encoding (A=1, Z=26)
    """
    rp = code5_A1Z26(pt_letter)
    rk = code5_A1Z26(key_letter)

    if rp == -1 or rk == -1:
        return '?'

    # Add mod 26, keeping in 1-26 range
    r = ((rp - 1) + (rk - 1)) % 26 + 1
    return from_1_26(r)


def vigenere_decrypt_letter(ct_letter, key_letter):
    """
    Vigenère decryption: PT = (CT - KEY) mod 26
    """
    rc = code5_A1Z26(ct_letter)
    rk = code5_A1Z26(key_letter)

    if rc == -1 or rk == -1:
        return '?'

    # Subtract mod 26, keeping in 1-26 range
    r = ((rc - 1) - (rk - 1)) % 26 + 1
    return from_1_26(r)


def beaufort_encrypt_letter(pt_letter, key_letter):
    """
    Beaufort encryption: CT = (KEY - PT) mod 26
    Note: Beaufort is self-inverse
    """
    rp = code5_A1Z26(pt_letter)
    rk = code5_A1Z26(key_letter)

    if rp == -1 or rk == -1:
        return '?'

    # KEY - PT mod 26
    r = ((rk - 1) - (rp - 1)) % 26 + 1
    return from_1_26(r)


def beaufort_decrypt_letter(ct_letter, key_letter):
    """
    Beaufort decryption: Same as encryption (self-inverse)
    """
    return beaufort_encrypt_letter(ct_letter, key_letter)


def vigenere_encrypt_string(plaintext, keystream):
    """Encrypt string using Vigenère"""
    if len(plaintext) != len(keystream):
        raise ValueError(f"Length mismatch: PT={len(plaintext)}, Key={len(keystream)}")

    result = []
    for pt_char, key_char in zip(plaintext, keystream):
        result.append(vigenere_encrypt_letter(pt_char, key_char))
    return ''.join(result)


def vigenere_decrypt_string(ciphertext, keystream):
    """Decrypt string using Vigenère"""
    if len(ciphertext) != len(keystream):
        raise ValueError(f"Length mismatch: CT={len(ciphertext)}, Key={len(keystream)}")

    result = []
    for ct_char, key_char in zip(ciphertext, keystream):
        result.append(vigenere_decrypt_letter(ct_char, key_char))
    return ''.join(result)


def beaufort_encrypt_string(plaintext, keystream):
    """Encrypt string using Beaufort"""
    if len(plaintext) != len(keystream):
        raise ValueError(f"Length mismatch: PT={len(plaintext)}, Key={len(keystream)}")

    result = []
    for pt_char, key_char in zip(plaintext, keystream):
        result.append(beaufort_encrypt_letter(pt_char, key_char))
    return ''.join(result)


def beaufort_decrypt_string(ciphertext, keystream):
    """Decrypt string using Beaufort (same as encrypt)"""
    return beaufort_encrypt_string(ciphertext, keystream)