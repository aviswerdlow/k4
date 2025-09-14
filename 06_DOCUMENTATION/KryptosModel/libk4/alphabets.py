"""
Alphabet utilities for K4 cryptosystem
Provides 25-letter (no X) and 26-letter alphabets with 5-bit encoding
"""

# Standard alphabets
ALPH26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPH25 = "ABCDEFGHIJKLMNOPQRSTUVWYZ"  # No X

# Create lookup dictionaries
C2I26 = {c: i for i, c in enumerate(ALPH26)}
I2C26 = {i: c for i, c in enumerate(ALPH26)}
C2I25 = {c: i for i, c in enumerate(ALPH25)}
I2C25 = {i: c for i, c in enumerate(ALPH25)}


def c2i26(c):
    """Convert character to index in 26-letter alphabet"""
    return C2I26.get(c.upper(), -1)


def i2c26(i):
    """Convert index to character in 26-letter alphabet"""
    return I2C26.get(i % 26, '?')


def c2i25(c):
    """Convert character to index in 25-letter alphabet"""
    return C2I25.get(c.upper(), -1)


def i2c25(i):
    """Convert index to character in 25-letter alphabet"""
    return I2C25.get(i % 25, '?')


def encode5(text, alphabet='26'):
    """
    Encode text to 5-bit values

    Args:
        text: Input text string
        alphabet: '25' or '26' letter alphabet

    Returns:
        List of 5-bit integers (0-31 for 26-letter, 0-24 for 25-letter)
    """
    if alphabet == '25':
        return [c2i25(c) for c in text.upper() if c in ALPH25]
    else:
        return [c2i26(c) for c in text.upper() if c in ALPH26]


def decode5(values, alphabet='26'):
    """
    Decode 5-bit values to text

    Args:
        values: List of 5-bit integers
        alphabet: '25' or '26' letter alphabet

    Returns:
        Decoded text string
    """
    if alphabet == '25':
        return ''.join(i2c25(v) for v in values)
    else:
        return ''.join(i2c26(v) for v in values)