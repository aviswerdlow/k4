#!/usr/bin/env python3
"""
Direction Test - Verify encrypt/decrypt directions are correct
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from zone_mask_v1.scripts.zone_runner import ZoneRunner
from zone_mask_v1.scripts.cipher_families import VigenereCipher, BeaufortCipher


def test_cipher_directions():
    """Test that cipher encrypt/decrypt are inverses"""
    print("Testing cipher directions...")
    
    # Test Vigenere
    v = VigenereCipher()
    plaintext = "TESTMESSAGE"
    key = "KEY"
    
    encrypted = v.encrypt(plaintext, key)
    decrypted = v.decrypt(encrypted, key)
    
    assert decrypted == plaintext, f"Vigenere round-trip failed: {plaintext} -> {encrypted} -> {decrypted}"
    print(f"✓ Vigenere: {plaintext} -> {encrypted} -> {decrypted}")
    
    # Test Beaufort
    b = BeaufortCipher()
    encrypted = b.encrypt(plaintext, key)
    decrypted = b.decrypt(encrypted, key)
    
    assert decrypted == plaintext, f"Beaufort round-trip failed: {plaintext} -> {encrypted} -> {decrypted}"
    print(f"✓ Beaufort: {plaintext} -> {encrypted} -> {decrypted}")


def test_zone_runner_direction():
    """Test that zone runner actually transforms the text"""
    print("\nTesting zone runner transformation...")
    
    # Load real ciphertext
    ct_path = Path(__file__).parent.parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
    with open(ct_path, 'r') as f:
        ciphertext = f.read().strip().upper()
    
    # Test manifest with simple cipher
    test_manifest = {
        "zones": {
            "head": {"start": 0, "end": 20},
            "mid": {"start": 34, "end": 62},
            "tail": {"start": 74, "end": 96}
        },
        "control": {
            "mode": "content",
            "indices": [64, 65, 66, 67, 68, 69, 70, 71, 72, 73]
        },
        "cipher": {
            "family": "vigenere",
            "keys": {
                "head": "A",
                "mid": "A",
                "tail": "A"
            },
            "schedule": "static"
        }
    }
    
    runner = ZoneRunner()
    runner.manifest = test_manifest
    runner.ciphertext = ciphertext
    
    # Key "A" should be identity for Vigenere
    plaintext = runner.decrypt()
    
    # Check zones are untransformed with key "A"
    print(f"CT[0:20]:   {ciphertext[0:20]}")
    print(f"PT[0:20]:   {plaintext[0:20]}")
    assert plaintext[0:20] == ciphertext[0:20], "Key 'A' should be identity"
    print("✓ Identity key produces no change (correct)")
    
    # Now test with real key
    test_manifest['cipher']['keys'] = {
        "head": "KRYPTOS",
        "mid": "KRYPTOS",
        "tail": "KRYPTOS"
    }
    
    runner = ZoneRunner()
    runner.manifest = test_manifest
    runner.ciphertext = ciphertext
    
    plaintext = runner.decrypt()
    
    # Should be different
    print(f"\nWith key KRYPTOS:")
    print(f"CT[0:20]:   {ciphertext[0:20]}")
    print(f"PT[0:20]:   {plaintext[0:20]}")
    
    if plaintext[0:20] == ciphertext[0:20]:
        print("❌ ERROR: Decrypt produces no change with non-identity key!")
        print("   The decrypt operation may not be working correctly.")
        return False
    else:
        print("✓ Non-identity key produces transformation")
    
    # Test round-trip
    re_encrypted = runner.encrypt(plaintext)
    if re_encrypted == ciphertext:
        print("✓ Round-trip successful")
    else:
        print("❌ Round-trip failed!")
        print(f"   Original CT: {ciphertext[:30]}...")
        print(f"   Re-encrypt:  {re_encrypted[:30]}...")
    
    return True


def test_control_indices():
    """Verify control indices are reading correct positions"""
    print("\nTesting control indices...")
    
    ct_path = Path(__file__).parent.parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
    with open(ct_path, 'r') as f:
        ciphertext = f.read().strip().upper()
    
    # Check what's at positions 64-73
    control_text = ciphertext[64:74]
    print(f"CT[64:74] = '{control_text}'")
    
    expected = "NYPVTTMZFP"
    if control_text == expected:
        print(f"✓ Control positions contain expected ciphertext: {expected}")
    else:
        print(f"❌ Control positions mismatch!")
        print(f"   Expected: {expected}")
        print(f"   Got:      {control_text}")
    
    # Check individual indices
    indices = [64, 65, 66, 67, 68, 69, 70, 71, 72, 73]
    chars = [ciphertext[i] for i in indices]
    control_from_indices = ''.join(chars)
    
    print(f"Control from indices {indices}: '{control_from_indices}'")
    assert control_from_indices == expected, "Index extraction mismatch"


def main():
    print("DIRECTION & INVARIANCE TESTS")
    print("=" * 60)
    
    # Test 1: Cipher directions
    test_cipher_directions()
    
    # Test 2: Zone runner transformation
    test_zone_runner_direction()
    
    # Test 3: Control indices
    test_control_indices()
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS:")
    print("If tests pass but BERLINCLOCK isn't found, the issue is likely:")
    print("1. Wrong operation order (mask->cipher vs cipher->mask)")
    print("2. Wrong keys or parameters")
    print("3. BERLINCLOCK appears elsewhere (shifted or transposed)")


if __name__ == '__main__':
    main()