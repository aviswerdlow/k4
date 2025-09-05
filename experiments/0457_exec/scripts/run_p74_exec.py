#!/usr/bin/env python3
"""
Run P[74] strip (A-Z) under publication policy.
Uses the real confirm harness from the main k4 CLI.
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
import csv
import string

def run_confirm(pt_path, out_dir):
    """Run the real confirm harness with publication policy."""
    
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
    print(f"Running P[74]={Path(pt_path).stem[-1]}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running confirm: {result.stderr}")
        return None
    
    # Parse the results
    coverage_report = Path(out_dir) / "coverage_report.json"
    if coverage_report.exists():
        with open(coverage_report) as f:
            return json.load(f)
    
    return None

def main():
    date_str = datetime.now().strftime("%Y%m%d")
    base_dir = Path(f"experiments/0457_exec/runs/{date_str}/p74_strip")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Get winner plaintext
    with open("experiments/0457_exec/data/pts/winner.txt") as f:
        winner_pt = f.read().strip()
    
    # Results for summary CSV
    results = []
    
    # Run for each letter A-Z
    for letter in string.ascii_uppercase:
        # Create plaintext with P[74]=letter
        pt_with_letter = winner_pt[:74] + letter + winner_pt[75:]
        
        # Save plaintext
        pt_path = base_dir / f"pt_{letter}.txt"
        with open(pt_path, 'w') as f:
            f.write(pt_with_letter)
        
        # Run confirm
        out_dir = base_dir / f"p74_{letter}"
        result = run_confirm(str(pt_path), str(out_dir))
        
        if result:
            # Extract key metrics
            row = {
                "P74": letter,
                "encrypts_to_ct": result.get("encrypts_to_ct", False),
                "and_pass": result.get("phrase_gate", {}).get("pass", False),
                "holm_cov_adj": result.get("nulls", {}).get("p_cov_holm", 1.0),
                "holm_fw_adj": result.get("nulls", {}).get("p_fw_holm", 1.0),
                "publishable": result.get("nulls", {}).get("publishable", False)
            }
            results.append(row)
    
    # Write summary CSV
    csv_path = base_dir / "P74_STRIP_SUMMARY.csv"
    with open(csv_path, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
            
            # Add editorial conclusion
            f.write("\n# Editorial conclusion: Based on earlier executed work, ")
            f.write("we expect equal treatment at P[74]. ")
            
            # Check if any letters show significance flip
            baseline_pub = results[ord('T') - ord('A')]['publishable'] if len(results) > 19 else False
            flips = [r for r in results if r['publishable'] != baseline_pub]
            
            if flips:
                f.write(f"WARNING: {len(flips)} letters show significance flip: ")
                f.write(", ".join([r['P74'] for r in flips]))
                f.write(". See individual bundles for details.")
            else:
                f.write("All 26 letters show identical publishability status.")
    
    print(f"\n=== P[74] strip complete ===")
    print(f"Results written to: {csv_path}")
    
    # Create manifest
    subprocess.run(["python3", "-m", "k4cli.cli", "manifest", "--dir", str(base_dir), "--out", str(base_dir / "MANIFEST.sha256")])
    
    # Write repro steps
    repro_path = base_dir / "REPRO_STEPS.md"
    with open(repro_path, 'w') as f:
        f.write("# P[74] Strip Reproduction Steps\n\n")
        f.write("## Command Used\n\n")
        f.write("```bash\n")
        f.write("python3 experiments/0457_exec/scripts/run_p74_exec.py\n")
        f.write("```\n\n")
        f.write("## Method\n\n")
        f.write("1. Take winner plaintext\n")
        f.write("2. For each letter A-Z, replace P[74] with that letter\n")
        f.write("3. Run publication policy (POS=0.60, ppct=1.0)\n")
        f.write("4. Record AND gate pass/fail and Holm-adjusted p-values\n\n")
        f.write("## Expected Result\n\n")
        f.write("All 26 letters should show equal treatment (editorial choice).\n")

if __name__ == "__main__":
    main()