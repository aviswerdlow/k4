#!/usr/bin/env python3

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / '03_SOLVERS' / 'zone_mask_v1' / 'scripts'))
from cipher_families_autokey import AutokeyVigenere

# Test PT-autokey
cipher = AutokeyVigenere('KEY', 'pt', 'kryptos')

plaintext = "ATTACKATDAWN"
print(f"Original plaintext: {plaintext}")
print(f"Seed key: KEY")
print(f"Full keystream should be: KEY{plaintext[:len(plaintext)-3]}")
print(f"                        = KEYATTACKATD")

# Manual encryption
alphabet = 'KRYPTOSABCDEFGHIJLMNQUVWXZ'
keystream = "KEYATTACKATD"
ciphertext = []

for i, p_char in enumerate(plaintext):
    k_char = keystream[i]
    p_pos = alphabet.index(p_char)
    k_pos = alphabet.index(k_char)
    c_pos = (p_pos + k_pos) % 26
    c_char = alphabet[c_pos]
    ciphertext.append(c_char)
    print(f"  {p_char}({p_pos:2d}) + {k_char}({k_pos:2d}) = {c_char}({c_pos:2d})")

manual_ct = ''.join(ciphertext)
print(f"\nManual ciphertext: {manual_ct}")

# Test with our implementation
actual_ct = cipher.encrypt(plaintext)
print(f"Actual ciphertext: {actual_ct}")

# Test decryption
decrypted = cipher.decrypt(actual_ct)
print(f"Decrypted:         {decrypted}")

# Manual decryption step by step
print("\nManual decryption:")
keystream_decrypt = list("KEY")
result = []
for i, c_char in enumerate(actual_ct):
    k_char = keystream_decrypt[i]
    c_pos = alphabet.index(c_char)
    k_pos = alphabet.index(k_char)
    p_pos = (c_pos - k_pos) % 26
    p_char = alphabet[p_pos]
    result.append(p_char)
    
    # Extend keystream with recovered plaintext
    if i >= 2:  # After seed key length - 1
        keystream_decrypt.append(p_char)
    
    print(f"  {c_char}({c_pos:2d}) - {k_char}({k_pos:2d}) = {p_char}({p_pos:2d})  keystream={''.join(keystream_decrypt)}")

manual_pt = ''.join(result)
print(f"\nManual plaintext: {manual_pt}")