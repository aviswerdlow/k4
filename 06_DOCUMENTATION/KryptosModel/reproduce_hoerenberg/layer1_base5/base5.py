"""
Base-5 modulo operations for Hörenberg's Layer 1
Implements the modulo-5 addition/subtraction on digit pairs
"""

from alph25 import letter_to_base5, base5_to_letter, string_to_base5


def base5_subtract(cipher_letter, key_letter, alphabet):
    """
    Base-5 decryption: plain = (cipher - key) mod 5 (digit-wise)

    This is Hörenberg's decryption operation for Layer 1

    Args:
        cipher_letter: Cipher letter
        key_letter: Key letter
        alphabet: 25-letter alphabet to use

    Returns:
        Plaintext letter
    """
    c_digits = letter_to_base5(cipher_letter, alphabet)
    k_digits = letter_to_base5(key_letter, alphabet)

    if not c_digits or not k_digits:
        return '?'

    # Subtract modulo 5 for each digit
    p_d1 = (c_digits[0] - k_digits[0]) % 5
    p_d0 = (c_digits[1] - k_digits[1]) % 5

    return base5_to_letter(p_d1, p_d0, alphabet)


def base5_add(plain_letter, key_letter, alphabet):
    """
    Base-5 encryption: cipher = (plain + key) mod 5 (digit-wise)

    Args:
        plain_letter: Plain letter
        key_letter: Key letter
        alphabet: 25-letter alphabet to use

    Returns:
        Cipher letter
    """
    p_digits = letter_to_base5(plain_letter, alphabet)
    k_digits = letter_to_base5(key_letter, alphabet)

    if not p_digits or not k_digits:
        return '?'

    # Add modulo 5 for each digit
    c_d1 = (p_digits[0] + k_digits[0]) % 5
    c_d0 = (p_digits[1] + k_digits[1]) % 5

    return base5_to_letter(c_d1, c_d0, alphabet)


def base5_decrypt_string(cipher_text, key_text, alphabet):
    """
    Decrypt a string using base-5 subtraction

    Args:
        cipher_text: Cipher string
        key_text: Key string (will be repeated if shorter)
        alphabet: 25-letter alphabet

    Returns:
        Plaintext string
    """
    result = []
    key_len = len(key_text)

    for i, c_char in enumerate(cipher_text):
        k_char = key_text[i % key_len] if key_len > 0 else 'A'
        p_char = base5_subtract(c_char, k_char, alphabet)
        result.append(p_char)

    return ''.join(result)


def base5_encrypt_string(plain_text, key_text, alphabet):
    """
    Encrypt a string using base-5 addition

    Args:
        plain_text: Plain string
        key_text: Key string (will be repeated if shorter)
        alphabet: 25-letter alphabet

    Returns:
        Cipher string
    """
    result = []
    key_len = len(key_text)

    for i, p_char in enumerate(plain_text):
        k_char = key_text[i % key_len] if key_len > 0 else 'A'
        c_char = base5_add(p_char, k_char, alphabet)
        result.append(c_char)

    return ''.join(result)