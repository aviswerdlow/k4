"""
Fixed base-5 masking layer for K4 cryptosystem
Operates on 25-letter alphabet (drop J) with CIAX key
"""

from alphabets_fixed import c2i25, i2c25, letter_to_base5, base5_to_letter, ALPH25


def base5_mask_letter(pt_letter, key_letter):
    """
    Mask a single letter using base-5 arithmetic

    Args:
        pt_letter: Plaintext letter (ALPH25)
        key_letter: Key letter (ALPH25)

    Returns:
        Masked letter (ALPH25)
    """
    pt_digits = letter_to_base5(pt_letter)
    key_digits = letter_to_base5(key_letter)

    if pt_digits is None or key_digits is None:
        return '?'

    # Add modulo 5 for each digit
    d1 = (pt_digits[0] + key_digits[0]) % 5
    d0 = (pt_digits[1] + key_digits[1]) % 5

    return base5_to_letter(d1, d0)


def base5_unmask_letter(masked_letter, key_letter):
    """
    Unmask a single letter using base-5 arithmetic

    Args:
        masked_letter: Masked letter (ALPH25)
        key_letter: Key letter (ALPH25)

    Returns:
        Original plaintext letter (ALPH25)
    """
    masked_digits = letter_to_base5(masked_letter)
    key_digits = letter_to_base5(key_letter)

    if masked_digits is None or key_digits is None:
        return '?'

    # Subtract modulo 5 for each digit
    d1 = (masked_digits[0] - key_digits[0]) % 5
    d0 = (masked_digits[1] - key_digits[1]) % 5

    return base5_to_letter(d1, d0)


def base5_mask_string(plaintext, key="CIAX"):
    """
    Apply base-5 mask to entire plaintext string

    Args:
        plaintext: String in ALPH25
        key: Mask key (default: CIAX)

    Returns:
        Masked string in ALPH25
    """
    # Ensure key is valid ALPH25
    key_clean = ''.join(c for c in key.upper() if c in ALPH25)
    if not key_clean:
        raise ValueError("Invalid mask key - no valid ALPH25 characters")

    # Clean plaintext to ALPH25
    pt_clean = ''.join(c for c in plaintext.upper() if c in ALPH25)

    result = []
    for i, pt_char in enumerate(pt_clean):
        key_char = key_clean[i % len(key_clean)]
        result.append(base5_mask_letter(pt_char, key_char))

    return ''.join(result)


def base5_unmask_string(masked_text, key="CIAX"):
    """
    Remove base-5 mask from entire string

    Args:
        masked_text: Masked string in ALPH25
        key: Mask key (default: CIAX)

    Returns:
        Original plaintext in ALPH25
    """
    # Ensure key is valid ALPH25
    key_clean = ''.join(c for c in key.upper() if c in ALPH25)
    if not key_clean:
        raise ValueError("Invalid mask key - no valid ALPH25 characters")

    # Clean masked text to ALPH25
    masked_clean = ''.join(c for c in masked_text.upper() if c in ALPH25)

    result = []
    for i, masked_char in enumerate(masked_clean):
        key_char = key_clean[i % len(key_clean)]
        result.append(base5_unmask_letter(masked_char, key_char))

    return ''.join(result)