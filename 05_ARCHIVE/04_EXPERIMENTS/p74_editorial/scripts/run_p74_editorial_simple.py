#!/usr/bin/env python3
"""
Simplified P74 Editorial Study - Test all letters quickly.
"""

import json
import csv
import hashlib
from pathlib import Path
from datetime import datetime
import string
import sys
sys.path.append(str(Path(__file__).parent))

from solve_schedule import ScheduleSolver

def main():
    """Run simplified P74 editorial study"""
    
    print("=" * 60)
    print("P74 Editorial Study - Simplified Version")
    print("Testing which P[74] letters can find lawful schedules")
    print("=" * 60)
    
    # Setup
    base_dir = Path("experiments/p74_editorial")
    date_str = datetime.now().strftime("%Y%m%d")
    run_dir = base_dir / "runs" / date_str
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    ct_path = base_dir / "data" / "ciphertext_97.txt"
    with open(ct_path) as f:
        ct = f.read().strip()
    
    winner_path = base_dir / "data" / "pts" / "winner.txt"
    with open(winner_path) as f:
        winner_pt = f.read().strip()
    
    # Set up route paths
    route_paths = {
        "GRID_W14_ROWS": base_dir / "data" / "permutations" / "GRID_W14_ROWS.json",
        "GRID_W10_NW": base_dir / "data" / "permutations" / "GRID_W10_NW.json"
    }
    
    # Initialize solver
    solver = ScheduleSolver(ct, route_paths)
    
    # Prepare CSV output
    csv_path = run_dir / "P74_EDITORIAL_MATRIX.csv"
    with open(csv_path, "w", newline="") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=[
            "P74", "feasible", "route_id", "classing", 
            "encrypts_to_ct", "and_pass", "holm_cov_adj", "holm_fw_adj",
            "publishable", "fail_reason"
        ])
        csv_writer.writeheader()
        
        # Process each letter
        feasible_count = 0
        
        for letter in string.ascii_uppercase:
            print(f"Testing P[74]={letter}... ", end="", flush=True)
            
            # Create plaintext with P[74]=letter
            pt = winner_pt[:74] + letter + winner_pt[75:]
            
            # Try to solve for lawful schedule
            schedules = solver.solve_for_plaintext(pt, max_schedules=1)
            
            if schedules:
                feasible_count += 1
                print(f"✓ FEASIBLE ({schedules[0]['route_id']}, {schedules[0]['classing']})")
                
                # Write row with schedule info
                csv_writer.writerow({
                    "P74": letter,
                    "feasible": True,
                    "route_id": schedules[0]["route_id"],
                    "classing": schedules[0]["classing"],
                    "encrypts_to_ct": True,
                    "and_pass": False,  # Would need full confirm pipeline
                    "holm_cov_adj": 1.0,  # Placeholder
                    "holm_fw_adj": 1.0,  # Placeholder
                    "publishable": False,  # Conservative default
                    "fail_reason": "not_evaluated"
                })
            else:
                print("✗ No lawful schedule found")
                
                # Write row for infeasible letter
                csv_writer.writerow({
                    "P74": letter,
                    "feasible": False,
                    "route_id": "",
                    "classing": "",
                    "encrypts_to_ct": False,
                    "and_pass": False,
                    "holm_cov_adj": 1.0,
                    "holm_fw_adj": 1.0,
                    "publishable": False,
                    "fail_reason": "no_feasible_schedule"
                })
    
    # Write minimal REPRO_STEPS
    repro_path = run_dir / "REPRO_STEPS.md"
    with open(repro_path, "w") as f:
        f.write(f"""# P74 Editorial Study - Simplified

Generated: {datetime.now().isoformat()}

## Summary
Tested all 26 letters at position 74 to find which can produce lawful schedules.

## Results
- Total letters tested: 26
- Letters with feasible schedules: {feasible_count}
- Letters marked publishable: 0 (requires full confirm pipeline)

## Note
This is a simplified run focusing on schedule feasibility.
Full AND gate and nulls evaluation would be needed for publishability determination.
""")
    
    # Create manifest
    manifest_path = run_dir / "MANIFEST.sha256"
    with open(manifest_path, "w") as manifest:
        for file_path in sorted(run_dir.rglob("*")):
            if file_path.is_file() and file_path != manifest_path:
                rel_path = file_path.relative_to(run_dir)
                with open(file_path, "rb") as f:
                    sha = hashlib.sha256(f.read()).hexdigest()
                manifest.write(f"{sha}  {rel_path}\n")
    
    # Summary
    print("\n" + "=" * 60)
    print("P74 Editorial Study Complete (Simplified)")
    print(f"Results saved to: {csv_path}")
    print(f"Total letters tested: 26")
    print(f"Letters with feasible schedules: {feasible_count}")
    
    if feasible_count == 0:
        print("\nConclusion: No P[74] letter can produce a lawful schedule")
        print("that encrypts to the ciphertext with the tested parameters.")
        print("This suggests the winner's fixed schedule is unique.")
    
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())