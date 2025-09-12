#!/usr/bin/env python3
"""
Run GRID controls (MAP/TRUE/FACT) using winner's proof digest.
Shows exact fail points in the validation pipeline.
"""

import json
import csv
from pathlib import Path
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(__file__))
from confirm_with_digest import run_confirm_with_digest, create_mini_bundle

def analyze_fail_point(result):
    """Determine exact fail point in the pipeline."""
    
    # Check lawfulness first
    if not result.get("encrypts_to_ct", False):
        return "lawfulness", "Failed to encrypt to correct ciphertext with winner's schedule"
    
    # Check rails
    if not result.get("rails_valid", False):
        return "rails", "Rails validation failed"
    
    # Check Flint v2
    flint_pass = "flint_v2" in result.get("phrase_gate", {}).get("accepted_by", [])
    if not flint_pass:
        return "flint", "Missing required semantic tokens (CODE not present)"
    
    # Check Generic
    generic_pass = "generic" in result.get("phrase_gate", {}).get("accepted_by", [])
    if not generic_pass:
        return "generic", "Failed statistical thresholds"
    
    # Check nulls
    if not result.get("nulls", {}).get("publishable", False):
        cov_p = result.get("nulls", {}).get("p_cov_holm", 1.0)
        fw_p = result.get("nulls", {}).get("p_fw_holm", 1.0)
        return "nulls", f"Failed significance: cov_p={cov_p:.4f}, fw_p={fw_p:.4f}"
    
    return "none", "Passed all gates (unexpected for controls)"

def create_summary(label, result, fail_point, fail_reason):
    """Create one-page summary for a control."""
    
    summary = [
        f"# Control Summary: {label}",
        "",
        f"## Lawfulness Check",
        f"- Encrypts to CT: {'✓' if result.get('encrypts_to_ct') else '✗'}",
        f"  (Using winner's key schedule)",
        "",
        f"## Rails Check",
        f"- Rails valid: {'✓' if result.get('rails_valid') else '✗'}",
        "",
        f"## Flint v2 Check",
    ]
    
    flint_pass = "flint_v2" in result.get("phrase_gate", {}).get("accepted_by", [])
    summary.append(f"- Status: {'✓ PASS' if flint_pass else '✗ FAIL'}")
    
    if not flint_pass:
        summary.append(f"- Missing: CODE (replaced with {label.split()[-1]})")
    
    summary.extend([
        "",
        f"## Generic Check"
    ])
    
    generic_pass = "generic" in result.get("phrase_gate", {}).get("accepted_by", [])
    summary.append(f"- Status: {'✓ PASS' if generic_pass else '✗ FAIL (or not evaluated)' }")
    
    if flint_pass and generic_pass:
        summary.extend([
            "",
            f"## Nulls Check"
        ])
        nulls = result.get("nulls", {})
        summary.extend([
            f"- Coverage Holm p: {nulls.get('p_cov_holm', 1.0):.4f}",
            f"- F-words Holm p: {nulls.get('p_fw_holm', 1.0):.4f}",
            f"- Publishable: {'✓' if nulls.get('publishable') else '✗'}"
        ])
    
    summary.extend([
        "",
        f"## Fail Point",
        f"**{fail_point.upper()}**: {fail_reason}"
    ])
    
    return "\n".join(summary)

def main():
    date_str = datetime.now().strftime("%Y%m%d")
    base_dir = Path(f"experiments/0457_exec/runs/{date_str}/controls_grid")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Winner's proof digest and policy
    proof_digest = "experiments/0457_exec/data/winner_proof_digest.json"
    policy_path = "experiments/0457_exec/policies/POLICY.publication.json"
    
    controls = [
        ("control_map", "IS A MAP"),
        ("control_true", "IS TRUE"),
        ("control_fact", "IS FACT")
    ]
    
    # Results for summary CSV
    results = []
    
    print("=== Running GRID Controls ===")
    print(f"Using winner's digest: {proof_digest}")
    print(f"Testing control phrases: MAP, TRUE, FACT")
    print(f"Expected: All should fail (lawfulness or Flint)")
    
    for filename, label in controls:
        pt_path = f"experiments/0457_exec/data/pts/{filename}.txt"
        out_dir = base_dir / filename
        
        print(f"\nTesting control: {label}")
        
        # Run confirm
        result = run_confirm_with_digest(
            policy_path,
            pt_path,
            proof_digest,
            str(out_dir),
            filename
        )
        
        if result:
            # Analyze fail point
            fail_point, fail_reason = analyze_fail_point(result)
            
            print(f"  Fail point: {fail_point} - {fail_reason}")
            
            # Create one-page summary
            summary = create_summary(label, result, fail_point, fail_reason)
            summary_path = base_dir / f"CONTROL_{filename.upper()}_SUMMARY.md"
            with open(summary_path, 'w') as f:
                f.write(summary)
            
            # Ensure mini-bundle is complete
            create_mini_bundle(str(out_dir), policy_path, result)
            
            # Add to CSV results
            row = {
                "label": label,
                "encrypts_to_ct": result.get("encrypts_to_ct", False),
                "flint_pass": "flint_v2" in result.get("phrase_gate", {}).get("accepted_by", []),
                "generic_pass": "generic" in result.get("phrase_gate", {}).get("accepted_by", []),
                "holm_cov_adj": result.get("nulls", {}).get("p_cov_holm", 1.0),
                "holm_fw_adj": result.get("nulls", {}).get("p_fw_holm", 1.0),
                "publishable": result.get("nulls", {}).get("publishable", False),
                "fail_point": fail_point
            }
            results.append(row)
    
    # Write summary CSV
    csv_path = base_dir / "CONTROLS_SUMMARY.csv"
    with open(csv_path, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    print(f"\n=== Controls complete ===")
    print(f"Results written to: {csv_path}")
    print(f"One-pagers created for each control")
    
    # Write repro steps
    repro_path = base_dir / "REPRO_STEPS.md"
    with open(repro_path, 'w') as f:
        f.write("# GRID Controls Reproduction Steps\n\n")
        f.write("## Command Used\n\n")
        f.write("```bash\n")
        f.write("python3 experiments/0457_exec/scripts/run_controls_digest.py\n")
        f.write("```\n\n")
        f.write("## Method\n\n")
        f.write("1. Used winner's verified proof_digest.json\n")
        f.write("2. Tested control phrases: MAP, TRUE, FACT\n")
        f.write("3. Identified exact fail points in pipeline\n")
        f.write("4. Created one-page summaries with fail analysis\n\n")
        f.write("## Expected Results\n\n")
        f.write("- MAP/TRUE/FACT: Fail at lawfulness or Flint\n")
        f.write("- Shows controls are properly rejected by validation\n")

if __name__ == "__main__":
    main()