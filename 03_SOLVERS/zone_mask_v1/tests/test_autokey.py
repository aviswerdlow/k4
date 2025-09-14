#!/usr/bin/env python3
"""
Unit tests for autokey cipher systems
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from cipher_families_autokey import (
    AutokeyVigenere, AutokeyBeaufort,
    create_autokey_cipher, encode, decode,
    vigenere_autokey_pt, vigenere_autokey_ct,
    beaufort_autokey_pt, beaufort_autokey_ct
)


def test_vigenere_pt_autokey():
    """Test Vigenere plaintext autokey"""
    print("Testing Vigenere PT-autokey...")
    
    # Test with KRYPTOS tableau
    cipher = AutokeyVigenere('KEY', 'pt', 'kryptos')
    
    plaintext = "ATTACKATDAWN"
    ciphertext = cipher.encrypt(plaintext)
    decrypted = cipher.decrypt(ciphertext)
    
    assert decrypted == plaintext, f"PT-autokey round-trip failed: {plaintext} -> {ciphertext} -> {decrypted}"
    print(f"  Plain:     {plaintext}")
    print(f"  Keystream: KEY{plaintext[:-3]}")
    print(f"  Cipher:    {ciphertext}")
    print(f"  Decrypted: {decrypted}")
    print("  ✓ Vigenere PT-autokey passed")


def test_vigenere_ct_autokey():
    """Test Vigenere ciphertext autokey"""
    print("\nTesting Vigenere CT-autokey...")
    
    # Test with KRYPTOS tableau
    cipher = AutokeyVigenere('KEY', 'ct', 'kryptos')
    
    plaintext = "ATTACKATDAWN"
    ciphertext = cipher.encrypt(plaintext)
    decrypted = cipher.decrypt(ciphertext)
    
    assert decrypted == plaintext, f"CT-autokey round-trip failed: {plaintext} -> {ciphertext} -> {decrypted}"
    print(f"  Plain:     {plaintext}")
    print(f"  Seed:      KEY")
    print(f"  Cipher:    {ciphertext}")
    print(f"  Decrypted: {decrypted}")
    print("  ✓ Vigenere CT-autokey passed")


def test_beaufort_pt_autokey():
    """Test Beaufort plaintext autokey"""
    print("\nTesting Beaufort PT-autokey...")
    
    # Test with KRYPTOS tableau
    cipher = AutokeyBeaufort('KEY', 'pt', 'kryptos')
    
    plaintext = "ATTACKATDAWN"
    ciphertext = cipher.encrypt(plaintext)
    decrypted = cipher.decrypt(ciphertext)
    
    assert decrypted == plaintext, f"Beaufort PT-autokey failed: {plaintext} -> {ciphertext} -> {decrypted}"
    print(f"  Plain:     {plaintext}")
    print(f"  Keystream: KEY{plaintext[:-3]}")
    print(f"  Cipher:    {ciphertext}")
    print(f"  Decrypted: {decrypted}")
    print("  ✓ Beaufort PT-autokey passed")


def test_beaufort_ct_autokey():
    """Test Beaufort ciphertext autokey"""
    print("\nTesting Beaufort CT-autokey...")
    
    # Test with KRYPTOS tableau
    cipher = AutokeyBeaufort('KEY', 'ct', 'kryptos')
    
    plaintext = "ATTACKATDAWN"
    ciphertext = cipher.encrypt(plaintext)
    decrypted = cipher.decrypt(ciphertext)
    
    assert decrypted == plaintext, f"Beaufort CT-autokey failed: {plaintext} -> {ciphertext} -> {decrypted}"
    print(f"  Plain:     {plaintext}")
    print(f"  Seed:      KEY")
    print(f"  Cipher:    {ciphertext}")
    print(f"  Decrypted: {decrypted}")
    print("  ✓ Beaufort CT-autokey passed")


def test_factory_functions():
    """Test factory functions"""
    print("\nTesting factory functions...")
    
    plaintext = "BERLINCLOCK"
    
    # Test Vigenere PT-autokey
    config = {
        'family': 'vigenere',
        'mode': 'pt',
        'seed_key': 'URANIA',
        'tableau': 'kryptos'
    }
    
    ciphertext = encode(plaintext, config)
    decrypted = decode(ciphertext, config)
    
    assert decrypted == plaintext, "Factory Vigenere PT failed"
    print(f"  Vigenere PT: {plaintext} -> {ciphertext} -> {decrypted}")
    
    # Test Beaufort CT-autokey
    config = {
        'family': 'beaufort',
        'mode': 'ct',
        'seed_key': 'AZIMUTH',
        'tableau': 'kryptos'
    }
    
    ciphertext = encode(plaintext, config)
    decrypted = decode(ciphertext, config)
    
    assert decrypted == plaintext, "Factory Beaufort CT failed"
    print(f"  Beaufort CT: {plaintext} -> {ciphertext} -> {decrypted}")
    
    print("  ✓ Factory functions passed")


def test_shorthand_functions():
    """Test shorthand convenience functions"""
    print("\nTesting shorthand functions...")
    
    plaintext = "EASTNORTHEAST"
    seed = "CLOCK"
    
    # Test all shorthand functions
    ct_vpt = vigenere_autokey_pt(plaintext, seed)
    ct_vct = vigenere_autokey_ct(plaintext, seed)
    ct_bpt = beaufort_autokey_pt(plaintext, seed)
    ct_bct = beaufort_autokey_ct(plaintext, seed)
    
    print(f"  Plain: {plaintext}, Seed: {seed}")
    print(f"  Vigenere PT: {ct_vpt}")
    print(f"  Vigenere CT: {ct_vct}")
    print(f"  Beaufort PT: {ct_bpt}")
    print(f"  Beaufort CT: {ct_bct}")
    
    # Verify they're all different (as expected)
    assert len(set([ct_vpt, ct_vct, ct_bpt, ct_bct])) == 4, "Shorthands should produce different outputs"
    print("  ✓ Shorthand functions passed")


def test_anchor_segments():
    """Test decryption at anchor positions"""
    print("\nTesting anchor position decryption...")
    
    # Load K4 ciphertext
    ct_path = Path(__file__).parent.parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
    with open(ct_path, 'r') as f:
        ciphertext = f.read().strip().upper()
    
    # Test a specific seed at anchor positions
    seed = "BERLIN"
    cipher = AutokeyVigenere(seed, 'pt', 'kryptos')
    
    # Decrypt segments at anchor positions
    segments = [
        (21, 24, "EAST"),
        (25, 33, "NORTHEAST"),
        (63, 68, "BERLIN"),
        (69, 73, "CLOCK")
    ]
    
    print(f"  Testing seed '{seed}' at anchor positions:")
    for start, end, expected in segments:
        ct_segment = ciphertext[start:end+1]
        pt_segment = cipher.decrypt(ct_segment)
        match = "✓" if pt_segment == expected else "✗"
        print(f"    {start:2d}-{end:2d}: {ct_segment} -> {pt_segment} (expected {expected}) {match}")
    
    print("  ✓ Anchor segment test complete")


def main():
    """Run all tests"""
    print("=" * 60)
    print("AUTOKEY CIPHER TESTS")
    print("=" * 60)
    
    tests = [
        test_vigenere_pt_autokey,
        test_vigenere_ct_autokey,
        test_beaufort_pt_autokey,
        test_beaufort_ct_autokey,
        test_factory_functions,
        test_shorthand_functions,
        test_anchor_segments
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n  ❌ {test.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)