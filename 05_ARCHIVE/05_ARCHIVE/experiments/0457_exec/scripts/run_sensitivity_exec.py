#!/usr/bin/env python3
"""
Run sensitivity strip (3x3 with 3 nulls replicates per cell).
Uses the real confirm harness from the main k4 CLI.
"""

import json
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
import csv

def run_confirm(policy_path, pt_path, route_path, out_dir, replicate=0):
    """Run the real confirm harness with specified parameters."""
    
    # Create output directory
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    
    # Build command for k4 confirm
    cmd = [
        "python3", "-m", "k4cli.cli", "confirm",
        "--ct", "experiments/0457_exec/data/ciphertext_97.txt",
        "--pt", pt_path,
        "--perm", route_path,
        "--cuts", "experiments/0457_exec/data/canonical_cuts.json",
        "--fwords", "experiments/0457_exec/data/function_words.txt",
        "--calib", "experiments/0457_exec/data/calib_97_perplexity.json",
        "--pos-trigrams", "experiments/0457_exec/data/pos_trigrams.json",
        "--pos-threshold", "experiments/0457_exec/data/pos_threshold.txt",
        "--policy", policy_path,
        "--out", out_dir
    ]
    
    # Add replicate tag if not baseline
    if replicate > 0:
        cmd.extend(["--nulls-replicate", str(replicate)])
    
    # Run the command
    print(f"Running: {' '.join(cmd)}")
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
    base_dir = Path(f"experiments/0457_exec/runs/{date_str}/sensitivity_strip")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Define candidates
    candidates = [
        ("winner", "experiments/0457_exec/data/pts/winner.txt", 
         "data/permutations/GRID_W14_ROWS.json")
    ]
    
    # Define policies (3x3 grid)
    policies = []
    for pos in ["055", "060", "065"]:
        for ppct in ["15", "10", "05"]:
            policy_file = f"POLICY.pos{pos}_pp{ppct}.json"
            policy_path = f"experiments/0457_exec/policies/sensitivity/{policy_file}"
            policies.append((pos, ppct, policy_path))
    
    # Results for matrix CSV
    results = []
    
    # Run each combination
    for pos, ppct, policy_path in policies:
        policy_dir = base_dir / f"pos{pos}_pp{ppct}"
        
        for label, pt_path, route_path in candidates:
            # Extract route ID from path
            route_id = Path(route_path).stem
            
            # Run 3 replicates
            for rep in range(3):
                out_dir = policy_dir / label / f"rep{rep}"
                
                print(f"\n=== Running {label} with pos={pos}, ppct={ppct}, replicate={rep} ===")
                result = run_confirm(policy_path, pt_path, route_path, str(out_dir), rep)
                
                if result:
                    # Extract key metrics
                    row = {
                        "policy": f"pos{pos}_pp{ppct}",
                        "pos": float(f"0.{pos}"),
                        "ppct": float(ppct) / 10.0,
                        "label": label,
                        "route_id": route_id,
                        "encrypts_to_ct": result.get("encrypts_to_ct", False),
                        "and_pass": result.get("phrase_gate", {}).get("pass", False),
                        "holm_cov_adj": result.get("nulls", {}).get("p_cov_holm", 1.0),
                        "holm_fw_adj": result.get("nulls", {}).get("p_fw_holm", 1.0),
                        "publishable": result.get("nulls", {}).get("publishable", False),
                        "replicate": rep
                    }
                    results.append(row)
    
    # Write matrix CSV
    csv_path = base_dir / "SENS_STRIP_MATRIX.csv"
    with open(csv_path, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    print(f"\n=== Sensitivity strip complete ===")
    print(f"Results written to: {csv_path}")
    
    # Create manifest
    subprocess.run(["python3", "-m", "k4cli.cli", "manifest", "--dir", str(base_dir), "--out", str(base_dir / "MANIFEST.sha256")])
    
    # Write repro steps
    repro_path = base_dir / "REPRO_STEPS.md"
    with open(repro_path, 'w') as f:
        f.write("# Sensitivity Strip Reproduction Steps\n\n")
        f.write("## Commands Used\n\n")
        f.write("```bash\n")
        f.write("python3 experiments/0457_exec/scripts/run_sensitivity_exec.py\n")
        f.write("```\n\n")
        f.write("## Policy Parameters\n\n")
        f.write("| Policy | POS | Perplexity % |\n")
        f.write("|--------|-----|-------------|\n")
        for pos, ppct, _ in policies:
            f.write(f"| pos{pos}_pp{ppct} | 0.{pos} | {float(ppct)/10}% |\n")
        f.write("\n## Replicates\n\n")
        f.write("- Replicate 0: Baseline seed (1337)\n")
        f.write("- Replicate 1: Nulls reseeded with |rep:1| tag\n")
        f.write("- Replicate 2: Nulls reseeded with |rep:2| tag\n")

if __name__ == "__main__":
    main()