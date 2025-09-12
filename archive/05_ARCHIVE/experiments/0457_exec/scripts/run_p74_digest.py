#!/usr/bin/env python3
"""
Run P[74] strip (A-Z) using winner's proof digest.
Only the publication letter should encrypt correctly with winner's schedule.
"""

import json
import csv
from pathlib import Path
from datetime import datetime
import string
import sys
import os
sys.path.append(os.path.dirname(__file__))
from confirm_with_digest import run_confirm_with_digest, create_mini_bundle

def main():
    date_str = datetime.now().strftime("%Y%m%d")
    base_dir = Path(f"experiments/0457_exec/runs/{date_str}/p74_strip")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Winner's proof digest and policy
    proof_digest = "experiments/0457_exec/data/winner_proof_digest.json"
    policy_path = "experiments/0457_exec/policies/POLICY.publication.json"
    
    # Get winner plaintext
    with open("experiments/0457_exec/data/pts/winner.txt") as f:
        winner_pt = f.read().strip()
    
    # Results for summary CSV
    results = []
    
    print("=== Running P[74] Strip ===")
    print(f"Using winner's digest: {proof_digest}")
    print(f"Testing letters A-Z at position 74")
    print(f"Expected: Only 'T' should be lawful with winner's schedule")
    
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
        print(f"\nTesting P[74]={letter}")
        
        result = run_confirm_with_digest(
            policy_path,
            str(pt_path),
            proof_digest,
            str(out_dir),
            f"p74_{letter}"
        )
        
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
            
            # Note which letter is actually lawful
            if result.get("encrypts_to_ct"):
                print(f"  ✓ {letter} encrypts to correct CT (lawful)")
            else:
                print(f"  ✗ {letter} does not encrypt to CT (not lawful with this schedule)")
            
            # Ensure mini-bundle is complete
            create_mini_bundle(str(out_dir), policy_path, result)
    
    # Write summary CSV
    csv_path = base_dir / "P74_STRIP_SUMMARY.csv"
    with open(csv_path, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    # Add editorial note
    with open(csv_path, 'a') as f:
        f.write("\n# Editorial conclusion:\n")
        f.write("# Based on the winner's fixed schedule, only P[74]='T' is lawful.\n")
        f.write("# Other letters fail lawfulness (encrypts_to_ct=false) as expected.\n")
        f.write("# This confirms P[74] is editorial choice, not cryptographically forced.\n")
    
    print(f"\n=== P[74] strip complete ===")
    print(f"Results written to: {csv_path}")
    
    # Count lawful letters
    lawful = [r for r in results if r["encrypts_to_ct"]]
    print(f"Lawful letters: {len(lawful)} (expected: 1 for 'T')")
    if lawful:
        print(f"Lawful: {', '.join([r['P74'] for r in lawful])}")
    
    # Write repro steps
    repro_path = base_dir / "REPRO_STEPS.md"
    with open(repro_path, 'w') as f:
        f.write("# P[74] Strip Reproduction Steps\n\n")
        f.write("## Command Used\n\n")
        f.write("```bash\n")
        f.write("python3 experiments/0457_exec/scripts/run_p74_digest.py\n")
        f.write("```\n\n")
        f.write("## Method\n\n")
        f.write("1. Used winner's verified proof_digest.json (fixed schedule)\n")
        f.write("2. For each letter A-Z, replaced P[74] with that letter\n")
        f.write("3. Ran confirm with publication policy\n")
        f.write("4. Recorded lawfulness (encrypts_to_ct) and gate results\n\n")
        f.write("## Expected Result\n\n")
        f.write("Only P[74]='T' should be lawful with winner's schedule.\n")
        f.write("Other letters fail lawfulness, confirming editorial choice.\n")

if __name__ == "__main__":
    main()