#!/usr/bin/env python3
"""
Unit tests for minimal masks (sparse_null and sparse_double)
"""

import sys
import random
import string
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from mask_library import SparseNull, SparseDouble


def generate_random_text(length: int) -> str:
    """Generate random uppercase text"""
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))


def test_sparse_null_round_trip():
    """Test sparse_null mask round-trip identity"""
    print("Testing sparse_null round-trip...")
    
    mask = SparseNull()
    
    # Test with K4 length (97 chars)
    for k in [5, 6, 7]:
        for r in range(k):
            params = {'k': k, 'r': r}
            
            # Test with random text
            original = generate_random_text(97)
            masked = mask.apply(original, params)
            unmasked = mask.invert(masked, params)
            
            assert unmasked == original, f"Round-trip failed for k={k}, r={r}"
            print(f"  ✓ k={k}, r={r}: Round-trip successful")
    
    print("  ✓ sparse_null round-trip tests passed")


def test_sparse_null_properties():
    """Test sparse_null mask properties"""
    print("\nTesting sparse_null properties...")
    
    mask = SparseNull()
    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    # Test k=6, r=2
    params = {'k': 6, 'r': 2}
    masked = mask.apply(text, params)
    
    # Check length preservation
    assert len(masked) == len(text), "Length not preserved"
    
    # Check that all characters are present
    assert sorted(masked) == sorted(text), "Characters changed"
    
    # Check that residue class is at the end
    expected_residue_chars = [text[i] for i in range(len(text)) if i % 6 == 2]
    actual_tail = masked[-len(expected_residue_chars):]
    assert sorted(actual_tail) == sorted(expected_residue_chars), "Residue class not at tail"
    
    print(f"  Original: {text}")
    print(f"  Masked:   {masked}")
    print(f"  Residue (i%6==2): {expected_residue_chars}")
    print("  ✓ sparse_null properties verified")


def test_sparse_double_round_trip():
    """Test sparse_double mask round-trip identity"""
    print("\nTesting sparse_double round-trip...")
    
    mask = SparseDouble()
    
    # Test with K4 length (97 chars)
    for k in [5, 6, 7]:
        for r in range(k):
            params = {'k': k, 'r': r}
            
            # Test with random text
            original = generate_random_text(97)
            masked = mask.apply(original, params)
            unmasked = mask.invert(masked, params)
            
            assert unmasked == original, f"Round-trip failed for k={k}, r={r}"
            print(f"  ✓ k={k}, r={r}: Round-trip successful")
    
    print("  ✓ sparse_double round-trip tests passed")


def test_sparse_double_properties():
    """Test sparse_double mask properties"""
    print("\nTesting sparse_double properties...")
    
    mask = SparseDouble()
    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    # Test k=6, r=2
    params = {'k': 6, 'r': 2}
    masked = mask.apply(text, params)
    
    # Check length preservation
    assert len(masked) == len(text), "Length not preserved"
    
    # Check that all characters are present
    assert sorted(masked) == sorted(text), "Characters changed"
    
    # Check that swaps occurred at residue positions
    residue_positions = [i for i in range(len(text)) if i % 6 == 2]
    print(f"  Original: {text}")
    print(f"  Masked:   {masked}")
    print(f"  Residue positions (i%6==2): {residue_positions}")
    
    # Verify specific swaps
    for j in range(0, len(residue_positions) - 1, 2):
        pos1 = residue_positions[j]
        pos2 = residue_positions[j + 1]
        assert masked[pos1] == text[pos2], f"Swap failed at {pos1}<->{pos2}"
        assert masked[pos2] == text[pos1], f"Swap failed at {pos1}<->{pos2}"
        print(f"    Swapped positions {pos1} and {pos2}: {text[pos1]}<->{text[pos2]}")
    
    print("  ✓ sparse_double properties verified")


def test_self_inverse():
    """Test that sparse_double is self-inverse"""
    print("\nTesting sparse_double self-inverse property...")
    
    mask = SparseDouble()
    text = generate_random_text(97)
    
    params = {'k': 7, 'r': 3}
    once = mask.apply(text, params)
    twice = mask.apply(once, params)
    
    assert twice == text, "sparse_double is not self-inverse"
    print("  ✓ sparse_double is self-inverse")


def test_k4_ciphertext():
    """Test masks on actual K4 ciphertext"""
    print("\nTesting on K4 ciphertext...")
    
    # Load K4 ciphertext
    ct_path = Path(__file__).parent.parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
    with open(ct_path, 'r') as f:
        k4_ct = f.read().strip().upper()
    
    print(f"  K4 ciphertext: {k4_ct[:40]}...")
    
    # Test sparse_null
    sn = SparseNull()
    params = {'k': 6, 'r': 2}
    sn_masked = sn.apply(k4_ct, params)
    sn_unmasked = sn.invert(sn_masked, params)
    assert sn_unmasked == k4_ct, "sparse_null failed on K4"
    print(f"  sparse_null k=6,r=2: {sn_masked[:40]}...")
    
    # Test sparse_double
    sd = SparseDouble()
    params = {'k': 7, 'r': 3}
    sd_masked = sd.apply(k4_ct, params)
    sd_unmasked = sd.invert(sd_masked, params)
    assert sd_unmasked == k4_ct, "sparse_double failed on K4"
    print(f"  sparse_double k=7,r=3: {sd_masked[:40]}...")
    
    print("  ✓ Masks work correctly on K4 ciphertext")


def main():
    """Run all tests"""
    print("=" * 60)
    print("MINIMAL MASK TESTS")
    print("=" * 60)
    
    tests = [
        test_sparse_null_round_trip,
        test_sparse_null_properties,
        test_sparse_double_round_trip,
        test_sparse_double_properties,
        test_self_inverse,
        test_k4_ciphertext
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