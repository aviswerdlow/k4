#!/usr/bin/env python3
"""
Validate core hardening study results.
"""

import json
import csv
import sys
from pathlib import Path


def validate_study(study_name, expected_feasible, expected_attempted):
    """Validate a single study's results."""
    study_dir = Path(f"04_EXPERIMENTS/core_hardening/{study_name}")
    
    # Check directory exists
    if not study_dir.exists():
        print(f"✗ {study_name}: Directory not found")
        return False
    
    # Check SUMMARY.json
    summary_path = study_dir / "SUMMARY.json"
    if not summary_path.exists():
        print(f"✗ {study_name}: SUMMARY.json not found")
        return False
    
    with open(summary_path, 'r') as f:
        summary = json.load(f)
    
    # Validate summary
    if summary['attempted'] != expected_attempted:
        print(f"✗ {study_name}: Expected {expected_attempted} attempted, got {summary['attempted']}")
        return False
    
    if summary['feasible'] != expected_feasible:
        print(f"✗ {study_name}: Expected {expected_feasible} feasible, got {summary['feasible']}")
        return False
    
    # Check RESULTS.csv exists
    results_path = study_dir / "RESULTS.csv"
    if not results_path.exists():
        print(f"✗ {study_name}: RESULTS.csv not found")
        return False
    
    # Count rows in CSV
    with open(results_path, 'r') as f:
        reader = csv.DictReader(f)
        row_count = sum(1 for _ in reader)
    
    if row_count != expected_attempted:
        print(f"✗ {study_name}: CSV has {row_count} rows, expected {expected_attempted}")
        return False
    
    # Check MANIFEST.sha256
    manifest_path = study_dir / "MANIFEST.sha256"
    if not manifest_path.exists():
        print(f"⚠ {study_name}: MANIFEST.sha256 not found")
    
    print(f"✓ {study_name}: Validated ({summary['feasible']}/{summary['attempted']} feasible)")
    return True


def main():
    """Main validation function."""
    print("=== Core Hardening Validation ===\n")
    
    all_valid = True
    
    # Validate each study
    studies = [
        ("skeleton_survey", 1, 24),
        ("tail_necessity", 0, 550),
        ("anchor_perturbations", 0, 27)
    ]
    
    for study_name, expected_feasible, expected_attempted in studies:
        if not validate_study(study_name, expected_feasible, expected_attempted):
            all_valid = False
    
    # Check baseline proof
    baseline_proof = Path("04_EXPERIMENTS/core_hardening/skeleton_survey/PROOFS/skeleton_S0_BASELINE.json")
    if baseline_proof.exists():
        with open(baseline_proof, 'r') as f:
            proof = json.load(f)
        
        if proof['class_formula'] == '((i%2)*3)+(i%3)':
            print(f"\n✓ Baseline proof verified")
        else:
            print(f"\n✗ Baseline proof has wrong formula")
            all_valid = False
    else:
        print(f"\n✗ Baseline proof not found")
        all_valid = False
    
    # Final summary
    print("\n" + "="*40)
    if all_valid:
        print("✅ All core hardening validations passed!")
        return 0
    else:
        print("❌ Some validations failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())