#!/usr/bin/env python3
"""
Test KRYPTOS-keyed tableau implementation
"""

import sys
from pathlib import Path

# Add path to cipher_families
sys.path.insert(0, str(Path(__file__).parent.parent.parent / '03_SOLVERS' / 'zone_mask_v1' / 'scripts'))
from cipher_families import VigenereCipher, BeaufortCipher


def test_kryptos_alphabet():
    """Test KRYPTOS-keyed alphabet construction"""
    cipher = VigenereCipher(tableau='kryptos')
    
    # First row should be KRYPTOS-keyed alphabet
    expected_first_row = 'KRYPTOSABCDEFGHIJLMNQUVWXZ'
    actual_first_row = cipher.tableau[0]
    
    print("Testing KRYPTOS-keyed alphabet:")
    print(f"  Expected: {expected_first_row}")
    print(f"  Actual:   {actual_first_row}")
    print(f"  Match: {actual_first_row == expected_first_row}")
    
    return actual_first_row == expected_first_row


def test_tableau_rotation():
    """Test that tableau rows are properly rotated"""
    cipher = VigenereCipher(tableau='kryptos')
    
    print("\nTesting tableau rotation:")
    print("First 5 rows of KRYPTOS tableau:")
    for i in range(5):
        print(f"  Row {i}: {cipher.tableau[i]}")
    
    # Check that each row is a rotation of the first
    first_row = cipher.tableau[0]
    for i in range(1, 26):
        expected = first_row[i:] + first_row[:i]
        actual = cipher.tableau[i]
        if expected != actual:
            print(f"  ERROR: Row {i} is not a proper rotation!")
            return False
    
    print("  All rows properly rotated ✓")
    return True


def test_vigenere_kryptos():
    """Test Vigenere encryption/decryption with KRYPTOS tableau"""
    print("\nTesting Vigenere with KRYPTOS tableau:")
    
    # Create cipher with KRYPTOS tableau
    cipher = VigenereCipher(tableau='kryptos')
    
    # Test encryption
    plaintext = "BERLINCLOCK"
    key = "PALIMPSEST"
    
    encrypted = cipher.encrypt(plaintext, key)
    print(f"  Plaintext:  {plaintext}")
    print(f"  Key:        {key}")
    print(f"  Encrypted:  {encrypted}")
    
    # Test decryption
    decrypted = cipher.decrypt(encrypted, key)
    print(f"  Decrypted:  {decrypted}")
    print(f"  Round-trip: {decrypted == plaintext}")
    
    return decrypted == plaintext


def test_beaufort_kryptos():
    """Test Beaufort encryption/decryption with KRYPTOS tableau"""
    print("\nTesting Beaufort with KRYPTOS tableau:")
    
    # Create cipher with KRYPTOS tableau
    cipher = BeaufortCipher(tableau='kryptos')
    
    # Test encryption (Beaufort is self-reciprocal)
    plaintext = "BERLINCLOCK"
    key = "PALIMPSEST"
    
    encrypted = cipher.encrypt(plaintext, key)
    print(f"  Plaintext:  {plaintext}")
    print(f"  Key:        {key}")
    print(f"  Encrypted:  {encrypted}")
    
    # Test decryption (should be same as encryption for Beaufort)
    decrypted = cipher.decrypt(encrypted, key)
    print(f"  Decrypted:  {decrypted}")
    print(f"  Round-trip: {decrypted == plaintext}")
    
    return decrypted == plaintext


def derive_required_key():
    """Derive the key required to produce BERLINCLOCK at positions 63-73"""
    print("\nDeriving required key for BERLINCLOCK with KRYPTOS tableau:")
    
    # Load the ciphertext fragment at positions 63-73
    ct_fragment = "NYPVTTMZFPK"  # From ciphertext at positions 63-73
    target = "BERLINCLOCK"
    
    print(f"  Ciphertext: {ct_fragment}")
    print(f"  Target:     {target}")
    
    # For Vigenere with KRYPTOS tableau
    cipher_vig = VigenereCipher(tableau='kryptos')
    
    # Derive key for Vigenere
    key_vig = []
    for i in range(len(ct_fragment)):
        ct_char = ct_fragment[i]
        pt_char = target[i]
        
        # Find which key letter would decrypt ct_char to pt_char
        for test_key_char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if cipher_vig.decrypt(ct_char, test_key_char) == pt_char:
                key_vig.append(test_key_char)
                break
    
    key_vig_str = ''.join(key_vig)
    print(f"\n  Required Vigenere key: {key_vig_str}")
    
    # Verify the key works
    test_decrypt = cipher_vig.decrypt(ct_fragment, key_vig_str)
    print(f"  Verification: {test_decrypt}")
    print(f"  Correct: {test_decrypt == target}")
    
    # For Beaufort with KRYPTOS tableau
    cipher_beau = BeaufortCipher(tableau='kryptos')
    
    # Derive key for Beaufort
    key_beau = []
    for i in range(len(ct_fragment)):
        ct_char = ct_fragment[i]
        pt_char = target[i]
        
        # Find which key letter would decrypt ct_char to pt_char
        for test_key_char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if cipher_beau.decrypt(ct_char, test_key_char) == pt_char:
                key_beau.append(test_key_char)
                break
    
    key_beau_str = ''.join(key_beau)
    print(f"\n  Required Beaufort key: {key_beau_str}")
    
    # Verify the key works
    test_decrypt = cipher_beau.decrypt(ct_fragment, key_beau_str)
    print(f"  Verification: {test_decrypt}")
    print(f"  Correct: {test_decrypt == target}")
    
    return key_vig_str, key_beau_str


def compare_tableaus():
    """Compare standard vs KRYPTOS tableau for the same operation"""
    print("\nComparing standard vs KRYPTOS tableau:")
    
    # Same plaintext and key
    plaintext = "BERLINCLOCK"
    key = "PALIMPSEST"
    
    # Standard tableau
    cipher_std = VigenereCipher(tableau='standard')
    encrypted_std = cipher_std.encrypt(plaintext, key)
    
    # KRYPTOS tableau
    cipher_kry = VigenereCipher(tableau='kryptos')
    encrypted_kry = cipher_kry.encrypt(plaintext, key)
    
    print(f"  Plaintext:     {plaintext}")
    print(f"  Key:           {key}")
    print(f"  Standard:      {encrypted_std}")
    print(f"  KRYPTOS:       {encrypted_kry}")
    print(f"  Different:     {encrypted_std != encrypted_kry}")
    
    return encrypted_std != encrypted_kry


def main():
    """Run all tests"""
    print("=" * 70)
    print("KRYPTOS TABLEAU UNIT TESTS")
    print("=" * 70)
    
    tests = [
        ("Alphabet construction", test_kryptos_alphabet),
        ("Tableau rotation", test_tableau_rotation),
        ("Vigenere round-trip", test_vigenere_kryptos),
        ("Beaufort round-trip", test_beaufort_kryptos),
        ("Tableau comparison", compare_tableaus)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\nERROR in {name}: {e}")
            results.append((name, False))
    
    # Derive required keys
    vig_key, beau_key = derive_required_key()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
    
    print("\nKEY FINDINGS:")
    print(f"  Required Vigenere key for BERLINCLOCK: {vig_key}")
    print(f"  Required Beaufort key for BERLINCLOCK: {beau_key}")
    
    # Check if these keys exist in any standard words
    test_keys = ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'ORDINATE', 'LATITUDE', 
                 'LONGITUDE', 'SHADOW', 'LIGHT', 'URANIA', 'WELTZEIT', 
                 'ALEXANDERPLATZ', 'BERLINCLOCK']
    
    print("\nSearching for key patterns in standard words:")
    for test_key in test_keys:
        if vig_key in test_key or test_key in vig_key:
            print(f"  Vigenere: {vig_key} found in/contains {test_key}")
        if beau_key in test_key or test_key in beau_key:
            print(f"  Beaufort: {beau_key} found in/contains {test_key}")


if __name__ == '__main__':
    main()