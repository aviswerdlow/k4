#!/usr/bin/env python3
"""
Quick test script to verify the K4 framework is working
"""

import json
from pathlib import Path

# Test imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / '03_SOLVERS'))

try:
    from zone_mask_v1.scripts.mask_library import apply_mask, create_mask
    from zone_mask_v1.scripts.route_engine import apply_route, create_route
    from zone_mask_v1.scripts.cipher_families import VigenereCipher, BeaufortCipher
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    exit(1)

# Test basic operations
def test_basic_operations():
    test_text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    # Test period-2 mask
    mask_config = {'type': 'period2', 'params': {'period': 2}}
    masked = apply_mask(test_text, mask_config)
    print(f"Period-2 mask: {test_text[:10]} -> {masked[:10]}")
    
    # Test Vigenere cipher
    cipher = VigenereCipher()
    key = "KEY"
    encrypted = cipher.encrypt(test_text, key)
    decrypted = cipher.decrypt(encrypted, key)
    assert decrypted == test_text, "Vigenere round-trip failed"
    print(f"✓ Vigenere round-trip successful")
    
    # Test Beaufort cipher
    cipher = BeaufortCipher()
    encrypted = cipher.encrypt(test_text, key)
    decrypted = cipher.decrypt(encrypted, key)
    assert decrypted == test_text, "Beaufort round-trip failed"
    print(f"✓ Beaufort round-trip successful")

# Create a simple test manifest
def create_test_manifest():
    manifest = {
        "zones": {
            "head": {"start": 0, "end": 20},
            "mid": {"start": 34, "end": 62},
            "tail": {"start": 74, "end": 96}
        },
        "control": {
            "mode": "content",
            "indices": [64, 65, 66, 67, 68, 69, 70, 71, 72, 73]
        },
        "mask": {
            "type": "period2",
            "params": {"period": 2}
        },
        "route": {
            "type": "columnar",
            "params": {"rows": 7, "cols": 14, "passes": 1}
        },
        "cipher": {
            "family": "vigenere",
            "keys": {
                "head": "ORDINATE",
                "mid": "ABSCISSA",
                "tail": "AZIMUTH"
            },
            "schedule": "static"
        }
    }
    
    # Save test manifest
    test_manifest_path = Path("test_manifest.json")
    with open(test_manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✓ Test manifest created: {test_manifest_path}")
    return test_manifest_path

if __name__ == "__main__":
    print("K4 Framework Test")
    print("-" * 40)
    
    # Run basic tests
    test_basic_operations()
    
    # Create test manifest
    manifest_path = create_test_manifest()
    
    print("-" * 40)
    print("Framework is ready!")
    print("\nNext steps:")
    print("1. Run experiments: make phase3-a")
    print("2. Verify solutions: make verify-rt MANIFEST=test_manifest.json")
    print("3. Generate notecard: make notecard MANIFEST=test_manifest.json")