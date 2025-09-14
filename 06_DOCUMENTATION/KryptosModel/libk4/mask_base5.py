"""
Base-5 masking layer for K4 cryptosystem
Operates on 25-letter alphabet (no X) with modulo 5 arithmetic
"""

from .alphabets import c2i25, i2c25, ALPH25


def base5_mask(plaintext, key):
    """
    Apply base-5 mask to plaintext using key

    Args:
        plaintext: Input text (25-letter alphabet)
        key: Masking key text (25-letter alphabet)

    Returns:
        Masked text as 5-bit values (0-24)
    """
    pt_vals = [c2i25(c) for c in plaintext.upper() if c in ALPH25]
    key_vals = [c2i25(c) for c in key.upper() if c in ALPH25]

    if not key_vals:
        return pt_vals

    masked = []
    for i, pt_val in enumerate(pt_vals):
        if pt_val == -1:
            continue
        key_val = key_vals[i % len(key_vals)]
        if key_val == -1:
            masked.append(pt_val)
        else:
            # Base-5 arithmetic: each position is a digit in base-5
            # Split into 5 groups of 5 letters each
            pt_base5 = [pt_val // 5, pt_val % 5]  # Convert to base-5 digits
            key_base5 = [key_val // 5, key_val % 5]

            # Add modulo 5 for each digit
            masked_base5 = [(pt_base5[j] + key_base5[j]) % 5 for j in range(2)]

            # Convert back to 0-24 range
            masked_val = masked_base5[0] * 5 + masked_base5[1]
            masked.append(masked_val)

    return masked


def base5_unmask(masked_values, key):
    """
    Remove base-5 mask from values using key

    Args:
        masked_values: List of masked 5-bit values (0-24)
        key: Masking key text (25-letter alphabet)

    Returns:
        Unmasked text string
    """
    key_vals = [c2i25(c) for c in key.upper() if c in ALPH25]

    if not key_vals:
        return ''.join(i2c25(v) for v in masked_values)

    unmasked = []
    for i, masked_val in enumerate(masked_values):
        key_val = key_vals[i % len(key_vals)]

        if key_val == -1:
            unmasked.append(i2c25(masked_val))
        else:
            # Base-5 arithmetic: reverse the masking
            masked_base5 = [masked_val // 5, masked_val % 5]
            key_base5 = [key_val // 5, key_val % 5]

            # Subtract modulo 5 for each digit
            pt_base5 = [(masked_base5[j] - key_base5[j]) % 5 for j in range(2)]

            # Convert back to 0-24 range
            pt_val = pt_base5[0] * 5 + pt_base5[1]
            unmasked.append(i2c25(pt_val))

    return ''.join(unmasked)