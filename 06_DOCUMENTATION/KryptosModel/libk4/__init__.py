"""
libk4: K4 two-layer cryptosystem implementation
Based on XOR + base-5 mask theory with panel row keys
"""

from .alphabets import ALPH25, ALPH26, encode5, decode5, c2i25, i2c25, c2i26, i2c26
from .mask_base5 import base5_mask, base5_unmask
from .xor5 import xor5_passthrough
from .cryptosystem import K4Cipher

__all__ = [
    'ALPH25', 'ALPH26',
    'encode5', 'decode5',
    'c2i25', 'i2c25', 'c2i26', 'i2c26',
    'base5_mask', 'base5_unmask',
    'xor5_passthrough',
    'K4Cipher'
]