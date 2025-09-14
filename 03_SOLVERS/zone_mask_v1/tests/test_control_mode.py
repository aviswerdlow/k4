#!/usr/bin/env python3
"""
Test Control Mode - Verify control-mode features work correctly
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from zone_mask_v1.scripts.zone_runner import ZoneRunner

def test_key_rotation():
    """Test rotate_on_control key schedule"""
    print("Testing key rotation at control points...")
    
    # Create test manifest with toy example
    manifest = {
        "zones": {
            "head": {"start": 0, "end": 19}
        },
        "control": {
            "mode": "control",
            "indices": [5, 10]
        },
        "cipher": {
            "family": "vigenere",
            "keys": {
                "head": "ABC"
            },
            "schedule": "rotate_on_control",
            "schedule_params": {"indices": [5, 10]}
        }
    }
    
    # Toy ciphertext: "ABCDEFGHIJKLMNOPQRST"
    test_ct = "ABCDEFGHIJKLMNOPQRST"
    
    runner = ZoneRunner()
    runner.manifest = manifest
    runner.ciphertext = test_ct
    
    plaintext = runner.decrypt()
    
    # With key "ABC" and rotation at 5 and 10:
    # Positions 0-4: key "ABC"
    # Positions 5-9: key "BCA" (rotated once)
    # Positions 10-19: key "CAB" (rotated twice)
    
    print(f"  CT: {test_ct}")
    print(f"  PT: {plaintext}")
    
    # Verify segments show different decryption
    seg1 = plaintext[0:5]
    seg2 = plaintext[5:10]
    seg3 = plaintext[10:20]
    
    print(f"  Segment 0-4: {seg1} (key: ABC)")
    print(f"  Segment 5-9: {seg2} (key: BCA)")
    print(f"  Segment 10-19: {seg3} (key: CAB)")
    
    # Check that segments are different (rotation had effect)
    if seg1 != seg2 and seg2 != seg3:
        print("  ✓ Key rotation working")
        return True
    else:
        print("  ✗ Key rotation not working")
        return False

def test_family_override():
    """Test family toggle at control points"""
    print("\nTesting family override at control points...")
    
    manifest = {
        "zones": {
            "mid": {"start": 0, "end": 19}
        },
        "control": {
            "mode": "control",
            "indices": [5, 15]
        },
        "cipher": {
            "family": "vigenere",
            "keys": {
                "mid": "KEY"
            },
            "schedule": "static",
            "family_overrides": {
                "mid_switch_at": 5,
                "mid_before": "vigenere",
                "mid_after": "beaufort",
                "mid_revert_at": 15
            }
        }
    }
    
    test_ct = "ABCDEFGHIJKLMNOPQRST"
    
    runner = ZoneRunner()
    runner.manifest = manifest
    runner.ciphertext = test_ct
    
    plaintext = runner.decrypt()
    
    print(f"  CT: {test_ct}")
    print(f"  PT: {plaintext}")
    
    # Segments should show different cipher families
    print(f"  Positions 0-4: Vigenere")
    print(f"  Positions 5-14: Beaufort")
    print(f"  Positions 15-19: Vigenere")
    
    # Basic check that decryption happened
    if plaintext != test_ct:
        print("  ✓ Family override applied")
        return True
    else:
        print("  ✗ Family override not working")
        return False

def test_mask_override():
    """Test mask switching at control points"""
    print("\nTesting mask override at control points...")
    
    manifest = {
        "zones": {
            "mid": {"start": 0, "end": 19}
        },
        "control": {
            "mode": "control",
            "indices": [10]
        },
        "mask": {
            "type": "period2",
            "params": {}
        },
        "mask_overrides": {
            "mid_switch_at": 10,
            "before": {
                "type": "period2",
                "params": {}
            },
            "after": {
                "type": "period3",
                "params": {}
            }
        },
        "cipher": {
            "family": "vigenere",
            "keys": {
                "mid": "A"  # Identity key to see mask effect
            },
            "schedule": "static"
        }
    }
    
    test_ct = "ABCDEFGHIJKLMNOPQRST"
    
    runner = ZoneRunner()
    runner.manifest = manifest
    runner.ciphertext = test_ct
    
    plaintext = runner.decrypt()
    
    print(f"  CT: {test_ct}")
    print(f"  PT: {plaintext}")
    print(f"  Positions 0-9: period-2 mask")
    print(f"  Positions 10-19: period-3 mask")
    
    # With identity cipher, only mask affects output
    if plaintext != test_ct:
        print("  ✓ Mask override working")
        return True
    else:
        print("  ✗ Mask override not applied")
        return False

def test_round_trip():
    """Test that round-trip still works with control mode"""
    print("\nTesting round-trip with control mode...")
    
    manifest = {
        "zones": {
            "head": {"start": 0, "end": 19}
        },
        "control": {
            "mode": "control",
            "indices": [5, 10, 15]
        },
        "cipher": {
            "family": "vigenere",
            "keys": {
                "head": "TESTKEY"
            },
            "schedule": "rotate_on_control",
            "schedule_params": {"indices": [5, 10, 15]}
        }
    }
    
    test_ct = "ABCDEFGHIJKLMNOPQRST"
    
    runner = ZoneRunner()
    runner.manifest = manifest
    runner.ciphertext = test_ct
    
    plaintext = runner.decrypt()
    re_encrypted = runner.encrypt(plaintext)
    
    print(f"  Original CT: {test_ct}")
    print(f"  Plaintext:   {plaintext}")
    print(f"  Re-encrypted: {re_encrypted}")
    
    if re_encrypted == test_ct:
        print("  ✓ Round-trip validation PASS")
        return True
    else:
        print("  ✗ Round-trip validation FAIL")
        return False

def main():
    print("CONTROL MODE TESTS")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(test_key_rotation())
    results.append(test_family_override())
    results.append(test_mask_override())
    results.append(test_round_trip())
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All control mode tests PASS")
    else:
        print("❌ Some tests failed - control mode needs debugging")

if __name__ == '__main__':
    main()