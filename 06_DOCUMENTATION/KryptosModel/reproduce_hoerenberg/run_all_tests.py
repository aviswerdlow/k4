#!/usr/bin/env python3
"""
Comprehensive test runner for Hörenberg K4 exact reproduction.
Validates Layer-2 exact match, Layer-1 CIAW reproduction, and infeasibility certificates.
"""

import sys
import subprocess


def run_test_suite(test_file, suite_name):
    """Run a test suite and return success status."""
    print(f"\n{'=' * 70}")
    print(f"Running: {suite_name}")
    print('=' * 70)

    result = subprocess.run(
        [sys.executable, test_file],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode == 0


def main():
    """Run all test suites and report overall status."""
    print("HÖRENBERG K4 EXACT REPRODUCTION - COMPREHENSIVE VALIDATION")
    print("=" * 70)

    test_suites = [
        ('test_reproduction.py', 'Layer-2 XOR Golden Tests'),
        ('test_mini_examples.py', 'Layer-1 Mini-Example Tests')
    ]

    all_passed = True
    results = {}

    for test_file, suite_name in test_suites:
        passed = run_test_suite(test_file, suite_name)
        results[suite_name] = passed
        if not passed:
            all_passed = False

    # Final summary
    print("\n" + "=" * 70)
    print("COMPREHENSIVE TEST SUMMARY")
    print("=" * 70)

    for suite_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{suite_name}: {status}")

    print("\n" + "-" * 70)

    if all_passed:
        print("\n🎉 ALL TESTS PASSED - EXACT REPRODUCTION VALIDATED")
        print("\nVerified Components:")
        print("✅ Layer-2 XOR: Exact P string and IoC (0.06077606)")
        print("✅ R27-31 Convention: Pass-through behavior confirmed")
        print("✅ Layer-1 CIAW: Exact reproduction with drop-X addition")
        print("📜 Layer-1 CIAX: No-solution certificate validated")
        print("📜 Layer-1 CULDWW: No-solution certificate validated")
        print("\nThe reproduction meets all 'no wiggle room' requirements:")
        print("• Exact IoC values for Layer-2")
        print("• Exact P strings for reproducible components")
        print("• Rigorous infeasibility proof for non-reproducible examples")
    else:
        print("\n❌ SOME TESTS FAILED - REVIEW REQUIRED")
        print("\nCheck individual test outputs above for details.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())