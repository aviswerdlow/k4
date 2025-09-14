"""
5-bit XOR layer with pass-through rule for K4 cryptosystem
Pass-through: If key bit is 0, plaintext bit passes through unchanged
"""


def xor5_passthrough(values, key_values):
    """
    Apply 5-bit XOR with pass-through rule

    Args:
        values: List of 5-bit integers (0-31)
        key_values: List of 5-bit key integers (0-31)

    Returns:
        List of XORed 5-bit integers
    """
    if not key_values:
        return values

    result = []
    for i, val in enumerate(values):
        key_val = key_values[i % len(key_values)]

        # XOR each bit position
        xor_val = 0
        for bit in range(5):
            val_bit = (val >> bit) & 1
            key_bit = (key_val >> bit) & 1

            # Pass-through rule: if key bit is 0, use plaintext bit
            # Otherwise, XOR the bits
            if key_bit == 0:
                result_bit = val_bit
            else:
                result_bit = val_bit ^ key_bit

            xor_val |= (result_bit << bit)

        result.append(xor_val)

    return result


def xor5_passthrough_decrypt(ciphertext_values, key_values):
    """
    Decrypt using 5-bit XOR with pass-through rule
    Note: For XOR with pass-through, decryption is the same as encryption

    Args:
        ciphertext_values: List of 5-bit ciphertext integers (0-31)
        key_values: List of 5-bit key integers (0-31)

    Returns:
        List of decrypted 5-bit integers
    """
    # XOR with pass-through is its own inverse
    return xor5_passthrough(ciphertext_values, key_values)