#!/usr/bin/env python3
"""
Run all tests for the K4 cryptanalysis framework.
"""

import sys
import os
import subprocess
from pathlib import Path


def run_test(test_path, description):
    """Run a single test file."""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Path: {test_path}")
    print('='*60)

    # Get absolute path
    abs_path = test_path.resolve()

    try:
        result = subprocess.run(
            [sys.executable, str(abs_path)],
            cwd=abs_path.parent,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print("✅ PASSED")
            return True
        else:
            print("❌ FAILED")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("⏱️ TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("K4 CRYPTANALYSIS TEST SUITE")
    print("="*60)

    # Find all test files
    test_files = [
        # Autokey tests
        ("03_SOLVERS/zone_mask_v1/tests/test_autokey.py",
         "Autokey Cipher Implementations"),

        # Layer-2 XOR tests
        ("03_SOLVERS/layer2_xor/tests/test_learn_rule.py",
         "Layer-2 Learned Keystream Rule"),

        # Layer-1 Base-5 tests
        ("03_SOLVERS/layer1_base5/tests/test_mini_examples.py",
         "Layer-1 Mini-Examples (CIAW/CIAX/CULDWW)"),

        # Tiny Mask + Classical tests
        ("03_SOLVERS/tiny_mask_classical/tests/test_tiny_mask_roundtrip.py",
         "Tiny Mask + Classical Round-trip"),
    ]

    # Track results
    passed = []
    failed = []

    # Run each test
    for test_file, description in test_files:
        test_path = Path(test_file)
        if test_path.exists():
            if run_test(test_path, description):
                passed.append(description)
            else:
                failed.append(description)
        else:
            print(f"\n⚠️ Test file not found: {test_file}")
            failed.append(f"{description} (NOT FOUND)")

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {len(passed)}")
    print(f"❌ Failed: {len(failed)}")

    if passed:
        print("\nPassed tests:")
        for test in passed:
            print(f"  ✓ {test}")

    if failed:
        print("\nFailed tests:")
        for test in failed:
            print(f"  ✗ {test}")

    # Exit code
    return 0 if len(failed) == 0 else 1


if __name__ == '__main__':
    sys.exit(main())