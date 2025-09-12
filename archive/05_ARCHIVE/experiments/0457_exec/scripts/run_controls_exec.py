#!/usr/bin/env python3
"""
Run GRID controls (MAP/TRUE/FACT) under publication policy.
Creates one-pagers showing exact fail point.
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
import csv

def run_confirm(pt_path, label, out_dir):
    """Run the real confirm harness and analyze fail points."""
    
    # Create output directory
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    
    # Build command for k4 confirm
    cmd = [
        "python3", "-m", "k4cli.cli", "confirm",
        "--ct", "experiments/0457_exec/data/ciphertext_97.txt",
        "--pt", pt_path,
        "--perm", "data/permutations/GRID_W14_ROWS.json",
        "--cuts", "experiments/0457_exec/data/canonical_cuts.json",
        "--fwords", "experiments/0457_exec/data/function_words.txt",
        "--calib", "experiments/0457_exec/data/calib_97_perplexity.json",
        "--pos-trigrams", "experiments/0457_exec/data/pos_trigrams.json",
        "--pos-threshold", "experiments/0457_exec/data/pos_threshold.txt",
        "--policy", "experiments/0457_exec/policies/POLICY.publication.json",
        "--out", out_dir
    ]
    
    # Run the command
    print(f"Running control: {label}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running confirm: {result.stderr}")
        return None
    
    # Parse all reports
    reports = {}
    for report_file in ["coverage_report.json", "phrase_gate_report.json", 
                        "near_gate_report.json", "holm_report_canonical.json"]:
        report_path = Path(out_dir) / report_file
        if report_path.exists():
            with open(report_path) as f:
                reports[report_file.replace(".json", "")] = json.load(f)
    
    return reports

def analyze_fail_point(reports):
    """Determine exact fail point in the pipeline."""
    
    if not reports:
        return "error", "Failed to run confirm"
    
    coverage = reports.get("coverage_report", {})
    phrase = reports.get("phrase_gate_report", {})
    
    # Check rails
    if not coverage.get("encrypts_to_ct", False):
        return "rails", "Failed to encrypt to correct ciphertext"
    
    if not coverage.get("rails_valid", False):
        return "rails", "Rails validation failed"
    
    # Check Flint v2
    flint_pass = "flint_v2" in phrase.get("accepted_by", [])
    if not flint_pass:
        # Find which Flint requirement failed
        flint_details = phrase.get("flint_v2", {})
        missing = []
        if not flint_details.get("has_direction"):
            missing.append("direction (EAST/NORTHEAST)")
        if not flint_details.get("has_verb"):
            missing.append("verb (READ/SEE/NOTE/SIGHT/OBSERVE)")
        if not flint_details.get("has_noun"):
            missing.append("noun (BERLIN/CLOCK/BERLINCLOCK/DIAL)")
        
        return "flint", f"Missing required tokens: {', '.join(missing) if missing else 'unknown'}"
    
    # Check Generic
    generic_pass = "generic" in phrase.get("accepted_by", [])
    if not generic_pass:
        generic_details = phrase.get("generic", {})
        ppct = generic_details.get("perplexity_percentile", 100)
        pos = generic_details.get("pos_trigram_score", 0)
        
        fail_reasons = []
        if ppct > 1.0:
            fail_reasons.append(f"perplexity_percentile={ppct:.2f}% > 1.0%")
        if pos < 0.60:
            fail_reasons.append(f"pos_score={pos:.3f} < 0.60")
        
        return "generic", f"Failed thresholds: {'; '.join(fail_reasons)}"
    
    # Check nulls
    nulls = coverage.get("nulls", {})
    if not nulls.get("publishable", False):
        cov_p = nulls.get("p_cov_holm", 1.0)
        fw_p = nulls.get("p_fw_holm", 1.0)
        return "nulls", f"Failed significance: cov_p={cov_p:.4f}, fw_p={fw_p:.4f} (need both < 0.01)"
    
    return "none", "Passed all gates"

def create_summary(label, reports, fail_point, fail_reason):
    """Create one-page summary for a control."""
    
    coverage = reports.get("coverage_report", {})
    phrase = reports.get("phrase_gate_report", {})
    
    summary = [
        f"# Control Summary: {label}",
        "",
        f"## Rails Check",
        f"- Encrypts to CT: {'✓' if coverage.get('encrypts_to_ct') else '✗'}",
        f"- Rails valid: {'✓' if coverage.get('rails_valid') else '✗'}",
        "",
        f"## Flint v2 Check",
    ]
    
    flint_pass = "flint_v2" in phrase.get("accepted_by", [])
    summary.append(f"- Status: {'✓ PASS' if flint_pass else '✗ FAIL'}")
    
    if not flint_pass and "flint_v2" in phrase:
        flint = phrase["flint_v2"]
        summary.extend([
            f"- Has direction: {'✓' if flint.get('has_direction') else '✗'}",
            f"- Has verb: {'✓' if flint.get('has_verb') else '✗'}",
            f"- Has noun: {'✓' if flint.get('has_noun') else '✗'}"
        ])
    
    summary.extend([
        "",
        f"## Generic Check"
    ])
    
    generic_pass = "generic" in phrase.get("accepted_by", [])
    summary.append(f"- Status: {'✓ PASS' if generic_pass else '✗ FAIL'}")
    
    if "generic" in phrase:
        generic = phrase["generic"]
        ppct = generic.get("perplexity_percentile", 100)
        pos = generic.get("pos_trigram_score", 0)
        summary.extend([
            f"- Perplexity percentile: {ppct:.2f}% (threshold: ≤1.0%)",
            f"- POS trigram score: {pos:.3f} (threshold: ≥0.60)"
        ])
    
    if flint_pass and generic_pass:
        summary.extend([
            "",
            f"## Nulls Check"
        ])
        nulls = coverage.get("nulls", {})
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
    
    controls = [
        ("control_map", "IS A MAP"),
        ("control_true", "IS TRUE"),
        ("control_fact", "IS FACT")
    ]
    
    # Results for summary CSV
    results = []
    
    for filename, label in controls:
        pt_path = f"experiments/0457_exec/data/pts/{filename}.txt"
        out_dir = base_dir / filename
        
        # Run confirm
        reports = run_confirm(pt_path, label, str(out_dir))
        
        if reports:
            # Analyze fail point
            fail_point, fail_reason = analyze_fail_point(reports)
            
            # Create one-page summary
            summary = create_summary(label, reports, fail_point, fail_reason)
            summary_path = base_dir / f"CONTROL_{filename.upper()}_SUMMARY.md"
            with open(summary_path, 'w') as f:
                f.write(summary)
            
            # Add to CSV results
            coverage = reports.get("coverage_report", {})
            phrase = reports.get("phrase_gate_report", {})
            nulls = coverage.get("nulls", {})
            
            row = {
                "label": label,
                "encrypts_to_ct": coverage.get("encrypts_to_ct", False),
                "flint_pass": "flint_v2" in phrase.get("accepted_by", []),
                "generic_pass": "generic" in phrase.get("accepted_by", []),
                "holm_cov_adj": nulls.get("p_cov_holm", 1.0),
                "holm_fw_adj": nulls.get("p_fw_holm", 1.0),
                "publishable": nulls.get("publishable", False),
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
    
    # Create manifest
    subprocess.run(["python3", "-m", "k4cli.cli", "manifest", "--dir", str(base_dir), "--out", str(base_dir / "MANIFEST.sha256")])
    
    # Write repro steps
    repro_path = base_dir / "REPRO_STEPS.md"
    with open(repro_path, 'w') as f:
        f.write("# GRID Controls Reproduction Steps\n\n")
        f.write("## Command Used\n\n")
        f.write("```bash\n")
        f.write("python3 experiments/0457_exec/scripts/run_controls_exec.py\n")
        f.write("```\n\n")
        f.write("## Controls Tested\n\n")
        f.write("1. **IS A MAP**: Replace 'CODE' with 'A MAP'\n")
        f.write("2. **IS TRUE**: Replace 'CODE' with 'TRUE'\n")
        f.write("3. **IS FACT**: Replace 'CODE' with 'FACT'\n\n")
        f.write("## Expected Results\n\n")
        f.write("Controls should fail at Flint v2 gate (missing required semantic tokens).\n")

if __name__ == "__main__":
    main()