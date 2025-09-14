#!/usr/bin/env python3
"""
Unit tests for paired alphabet cipher systems
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from cipher_families_pair import (
    KeyedAlphabet, PortaCipher, QuagmireCipher, 
    create_paired_cipher, encode, decode
)


def test_keyed_alphabet():
    """Test keyed alphabet generation"""
    print("Testing keyed alphabet generation...")
    
    # Test standard alphabet
    standard = KeyedAlphabet.create()
    assert standard == 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "Standard alphabet failed"
    
    # Test KRYPTOS keyed alphabet
    kryptos = KeyedAlphabet.create(alphabet_type='kryptos')
    assert kryptos == 'KRYPTOSABCDEFGHIJLMNQUVWXZ', "KRYPTOS alphabet failed"
    
    # Test custom keyword
    custom = KeyedAlphabet.create('BERLIN')
    assert custom == 'BERLINACDFGHJKMOPQSTUVWXYZ', "Custom keyword failed"
    
    print("  ✓ Keyed alphabet tests passed")


def test_porta_cipher():
    """Test Porta cipher encryption/decryption"""
    print("\nTesting Porta cipher...")
    
    # Basic Porta test
    porta = PortaCipher(row_alphabet='standard', indicator_key='KEY')
    
    plaintext = "ATTACKATDAWN"
    ciphertext = porta.encrypt(plaintext)
    decrypted = porta.decrypt(ciphertext)
    
    assert decrypted == plaintext, f"Porta round-trip failed: {plaintext} -> {ciphertext} -> {decrypted}"
    print(f"  Plain:  {plaintext}")
    print(f"  Cipher: {ciphertext}")
    print(f"  Decrypted: {decrypted}")
    
    # Test with KRYPTOS alphabet
    porta_k = PortaCipher(row_alphabet='kryptos', indicator_key='BERLIN')
    plaintext2 = "EASTBERLIN"
    ciphertext2 = porta_k.encrypt(plaintext2)
    decrypted2 = porta_k.decrypt(ciphertext2)
    
    assert decrypted2 == plaintext2, "Porta with KRYPTOS failed"
    print(f"  KRYPTOS test: {plaintext2} -> {ciphertext2} -> {decrypted2}")
    
    print("  ✓ Porta cipher tests passed")


def test_quagmire_ciphers():
    """Test Quagmire II, III, IV variants"""
    print("\nTesting Quagmire ciphers...")
    
    plaintext = "HELLOWORLD"
    indicator = "KEY"
    
    for variant in [2, 3, 4]:
        print(f"\n  Quagmire {variant}:")
        
        # Create cipher
        quag = QuagmireCipher(
            variant=variant,
            row_alphabet='kryptos',
            col_alphabet='kryptos',
            indicator_key=indicator
        )
        
        # Test encryption/decryption
        ciphertext = quag.encrypt(plaintext)
        decrypted = quag.decrypt(ciphertext)
        
        print(f"    Plain:  {plaintext}")
        print(f"    Cipher: {ciphertext}")
        print(f"    Decrypted: {decrypted}")
        
        assert decrypted == plaintext, f"Quagmire {variant} round-trip failed"
    
    print("\n  ✓ Quagmire cipher tests passed")


def test_factory_functions():
    """Test factory functions for creating ciphers"""
    print("\nTesting factory functions...")
    
    # Test Porta creation
    config_porta = {
        'family': 'porta',
        'alph_row': 'kryptos',
        'indicator': {'type': 'periodic', 'key': 'CLOCK'}
    }
    
    plaintext = "BERLINCLOCK"
    ciphertext = encode(plaintext, config_porta)
    decrypted = decode(ciphertext, config_porta)
    
    assert decrypted == plaintext, "Factory Porta failed"
    print(f"  Porta: {plaintext} -> {ciphertext} -> {decrypted}")
    
    # Test Quagmire creation
    for variant in [2, 3, 4]:
        config_quag = {
            'family': f'quag{variant}',
            'alph_row': 'kryptos',
            'alph_col': {'keyword': 'URANIA'},
            'indicator': {'type': 'periodic', 'key': 'EAST', 'phase': 0}
        }
        
        ciphertext = encode(plaintext, config_quag)
        decrypted = decode(ciphertext, config_quag)
        
        assert decrypted == plaintext, f"Factory Quagmire {variant} failed"
        print(f"  Quag{variant}: {plaintext} -> {ciphertext} -> {decrypted}")
    
    print("\n  ✓ Factory function tests passed")


def test_indicator_modes():
    """Test different indicator configurations"""
    print("\nTesting indicator modes...")
    
    plaintext = "EASTNORTHEASTBERLINCLOCK"
    
    # Static indicator
    config_static = {
        'family': 'porta',
        'alph_row': 'kryptos',
        'indicator': {'type': 'static'}
    }
    
    ct_static = encode(plaintext, config_static)
    pt_static = decode(ct_static, config_static)
    assert pt_static == plaintext, "Static indicator failed"
    
    # Periodic indicator with different phases
    for phase in [0, 1, 2]:
        config_periodic = {
            'family': 'porta',
            'alph_row': 'kryptos',
            'indicator': {'type': 'periodic', 'key': 'URANIA', 'phase': phase}
        }
        
        ct = encode(plaintext, config_periodic)
        pt = decode(ct, config_periodic)
        assert pt == plaintext, f"Periodic indicator phase {phase} failed"
    
    print("  ✓ Indicator mode tests passed")


def main():
    """Run all tests"""
    print("=" * 60)
    print("PAIRED ALPHABET CIPHER TESTS")
    print("=" * 60)
    
    tests = [
        test_keyed_alphabet,
        test_porta_cipher,
        test_quagmire_ciphers,
        test_factory_functions,
        test_indicator_modes
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