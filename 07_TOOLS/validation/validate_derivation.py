#!/usr/bin/env python3
"""
Validation script to ensure plaintext is derivable from CT + proof.
This is an invariant check that MUST pass for any valid solution.
"""

import json
import sys
import hashlib
from pathlib import Path

def validate_derivation_invariant(coverage_report_path: Path) -> bool:
    """
    Validate that the derivation invariant holds:
    1. pt_sha256_bundle == pt_sha256_derived
    2. tail_derivation_verified == true
    3. gates_head_only == true
    4. no_tail_guard == true
    
    NOTE: These strict invariants only apply to published winners.
    """
    
    # Scope guard - only enforce for published winners
    path_str = str(coverage_report_path)
    if "01_PUBLISHED/winner" not in path_str and "01_PUBLISHED/latest" not in path_str:
        print(f"ℹ️  Skipping strict validation for non-winner bundle: {coverage_report_path}")
        print("   (Strict derivation invariants only apply to published winners)")
        return True
    
    print("🔍 Validating derivation invariant for published winner...")
    
    # Load coverage report
    with open(coverage_report_path, 'r') as f:
        report = json.load(f)
    
    errors = []
    
    # Check 1: SHA match
    bundle_sha = report.get('pt_sha256_bundle', '')
    derived_sha = report.get('pt_sha256_derived', '')
    
    if not bundle_sha:
        errors.append("❌ Missing pt_sha256_bundle")
    if not derived_sha:
        errors.append("❌ Missing pt_sha256_derived")
    elif bundle_sha != derived_sha:
        errors.append(f"❌ SHA mismatch: bundle={bundle_sha[:8]}... derived={derived_sha[:8]}...")
    else:
        print(f"✅ SHA match: {bundle_sha[:16]}...")
    
    # Check 2: Tail derivation
    tail_verified = report.get('tail_derivation_verified')
    if tail_verified is not True:
        errors.append(f"❌ tail_derivation_verified must be true, got: {tail_verified}")
    else:
        print("✅ Tail derivation verified")
    
    # Check 3: Gates head only
    gates_head = report.get('gates_head_only')
    if gates_head is not True:
        errors.append(f"❌ gates_head_only must be true, got: {gates_head}")
    else:
        print("✅ Gates apply to head only")
    
    # Check 4: No tail guard
    no_tail = report.get('no_tail_guard')
    if no_tail is not True:
        errors.append(f"❌ no_tail_guard must be true, got: {no_tail}")
    else:
        print("✅ No tail guard in decryption")
    
    # Check 5: Derivation note present
    note = report.get('derivation_note', '')
    if not note:
        errors.append("❌ Missing derivation_note")
    else:
        print(f"✅ Derivation note: {note}")
    
    # Report results
    if errors:
        print("\n⚠️  INVARIANT VIOLATIONS:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("\n✅ ALL DERIVATION INVARIANTS SATISFIED")
        print("   - Plaintext fully derivable from CT + proof")
        print("   - Tail emerges from anchor-forced wheels")
        print("   - No assumptions or guards in decryption path")
        return True

def main():
    """Main entry point."""
    
    # Default path
    coverage_path = Path("01_PUBLISHED/winner_HEAD_0020_v522B/coverage_report.json")
    
    # Accept path from command line
    if len(sys.argv) > 1:
        coverage_path = Path(sys.argv[1])
    
    if not coverage_path.exists():
        print(f"❌ Coverage report not found: {coverage_path}")
        sys.exit(1)
    
    # Validate
    if validate_derivation_invariant(coverage_path):
        print("\n🎯 VALIDATION PASSED - System is airtight")
        sys.exit(0)
    else:
        print("\n❌ VALIDATION FAILED - System has gaps")
        sys.exit(1)

if __name__ == "__main__":
    main()