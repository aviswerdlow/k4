"""
Fixed alphabet utilities for K4 cryptosystem
Uses 25-letter alphabet with J dropped (not X)
"""

# 25-letter alphabet (drop J, keep X)
ALPH25 = "ABCDEFGHIKLMNOPQRSTUVWXYZ"

# Standard 26-letter alphabet
ALPH26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Create lookup dictionaries
C2I25 = {c: i for i, c in enumerate(ALPH25)}
I2C25 = {i: c for i, c in enumerate(ALPH25)}
C2I26 = {c: i for i, c in enumerate(ALPH26)}
I2C26 = {i: c for i, c in enumerate(ALPH26)}


def c2i25(c):
    """Convert character to index in 25-letter alphabet (0-24)"""
    return C2I25.get(c.upper(), -1)


def i2c25(i):
    """Convert index to character in 25-letter alphabet"""
    return I2C25.get(i % 25, '?')


def code5_A1Z26(letter):
    """Convert A..Z to 1..26 (5-bit code)"""
    idx = C2I26.get(letter.upper(), -1)
    if idx == -1:
        return -1
    return idx + 1  # A=1, B=2, ..., Z=26


def from_1_26(n):
    """Convert 1..26 back to A..Z"""
    if 1 <= n <= 26:
        return ALPH26[n - 1]
    return '?'


def letter_to_base5(letter):
    """Convert ALPH25 letter to (d1, d0) base-5 digits"""
    idx = c2i25(letter)
    if idx == -1:
        return None
    d1 = idx // 5
    d0 = idx % 5
    return (d1, d0)


def base5_to_letter(d1, d0):
    """Convert base-5 digits to ALPH25 letter"""
    idx = d1 * 5 + d0
    if 0 <= idx < 25:
        return i2c25(idx)
    return '?'