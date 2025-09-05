#!/usr/bin/env python3
"""
Run sensitivity strip using winner's proof digest.
3x3 grid with 3 nulls replicates per cell.
"""

import json
import csv
from pathlib import Path
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(__file__))
from confirm_with_digest import run_confirm_with_digest, create_mini_bundle

def main():
    date_str = datetime.now().strftime("%Y%m%d")
    base_dir = Path(f"experiments/0457_exec/runs/{date_str}/sensitivity_strip")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Winner's proof digest
    proof_digest = "experiments/0457_exec/data/winner_proof_digest.json"
    
    # Candidates
    candidates = [
        ("winner", "experiments/0457_exec/data/pts/winner.txt")
    ]
    
    # Policies (3x3 grid)
    policies = []
    for pos in ["055", "060", "065"]:
        for ppct in ["15", "10", "05"]:
            policy_file = f"POLICY.pos{pos}_pp{ppct}.json"
            policy_path = f"experiments/0457_exec/policies/sensitivity/{policy_file}"
            policies.append((pos, ppct, policy_path))
    
    # Results for matrix CSV
    results = []
    
    print("=== Running Sensitivity Strip ===")
    print(f"Using winner's digest: {proof_digest}")
    print(f"Total runs: {len(policies) * len(candidates) * 3}")
    
    # Run each combination
    for pos, ppct, policy_path in policies:
        policy_dir = base_dir / f"pos{pos}_pp{ppct}"
        
        for label, pt_path in candidates:
            # Run 3 replicates
            for rep in range(3):
                out_dir = policy_dir / label / f"rep{rep}"
                
                print(f"\nRunning {label} with pos={pos}/100, ppct={ppct}/10%, replicate={rep}")
                
                # Create unique label for this run
                run_label = f"{label}_pos{pos}_pp{ppct}_rep{rep}"
                
                # Run confirm with digest
                result = run_confirm_with_digest(
                    policy_path, 
                    pt_path, 
                    proof_digest, 
                    str(out_dir),
                    run_label
                )
                
                if result:
                    # Extract key metrics
                    row = {
                        "policy": f"pos{pos}_pp{ppct}",
                        "pos": float(f"0.{pos}"),
                        "ppct": float(ppct) / 10.0,
                        "label": label,
                        "route_id": "GRID_W14_ROWS",
                        "encrypts_to_ct": result.get("encrypts_to_ct", False),
                        "and_pass": result.get("phrase_gate", {}).get("pass", False),
                        "holm_cov_adj": result.get("nulls", {}).get("p_cov_holm", 1.0),
                        "holm_fw_adj": result.get("nulls", {}).get("p_fw_holm", 1.0),
                        "publishable": result.get("nulls", {}).get("publishable", False),
                        "replicate": rep
                    }
                    results.append(row)
                    
                    # Ensure mini-bundle is complete
                    create_mini_bundle(str(out_dir), policy_path, result)
    
    # Write matrix CSV
    csv_path = base_dir / "SENS_STRIP_MATRIX.csv"
    with open(csv_path, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    print(f"\n=== Sensitivity strip complete ===")
    print(f"Results written to: {csv_path}")
    print(f"Total bundles created: {len(results)}")
    
    # Write repro steps
    repro_path = base_dir / "REPRO_STEPS.md"
    with open(repro_path, 'w') as f:
        f.write("# Sensitivity Strip Reproduction Steps\n\n")
        f.write("## Commands Used\n\n")
        f.write("```bash\n")
        f.write("python3 experiments/0457_exec/scripts/run_sensitivity_digest.py\n")
        f.write("```\n\n")
        f.write("## Method\n\n")
        f.write("1. Used winner's verified proof_digest.json (GRID_W14_ROWS)\n")
        f.write("2. Fixed key schedules from winner's confirmation\n")
        f.write("3. Varied only the policy thresholds (POS and perplexity)\n")
        f.write("4. Ran 3 nulls replicates per cell (deterministic reseeding)\n\n")
        f.write("## Policy Parameters\n\n")
        f.write("| Policy | POS | Perplexity % |\n")
        f.write("|--------|-----|-------------|\n")
        for pos, ppct, _ in policies:
            f.write(f"| pos{pos}_pp{ppct} | 0.{pos} | {float(ppct)/10}% |\n")

if __name__ == "__main__":
    main()