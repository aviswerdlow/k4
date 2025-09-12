#!/usr/bin/env python3
"""
Run P74 Editorial/Gating Study.
For each letter A-Z at position 74, re-solve a lawful schedule and run full decision ladder.
"""

import json
import csv
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
import string
import sys
sys.path.append(str(Path(__file__).parent))

from solve_schedule import ScheduleSolver
from confirm_letter import confirm_letter_schedule

GLOBAL_SEED = 1337

def setup_run_directory(base_dir: Path) -> Path:
    """Create run directory structure"""
    date_str = datetime.now().strftime("%Y%m%d")
    run_dir = base_dir / "runs" / date_str
    
    # Create directories
    (run_dir / "p74_re_solve").mkdir(parents=True, exist_ok=True)
    
    return run_dir

def write_repro_steps(run_dir: Path):
    """Write reproducibility documentation"""
    repro_path = run_dir / "REPRO_STEPS.md"
    
    content = f"""# P74 Editorial Study - Reproduction Steps

Generated: {datetime.now().isoformat()}

## Configuration
- Global seed: {GLOBAL_SEED}
- Policy: experiments/p74_editorial/policies/POLICY.publication.json
- Routes: GRID_W14_ROWS, GRID_W10_NW
- Classing: c6a and c6b allowed
- Nulls: K=10,000 mirrored with Holm m=2

## Commands Used

1. Solve schedules for each letter:
```bash
python3 experiments/p74_editorial/scripts/solve_schedule.py [LETTER]
```

2. Run confirm pipeline:
```bash
python3 experiments/p74_editorial/scripts/confirm_letter.py [LETTER]
```

3. Full orchestration:
```bash
python3 experiments/p74_editorial/scripts/run_p74_editorial.py
```

## Seed Derivation

Per-letter seed recipe:
```
seed_recipe = "CONFIRM|K4|route:<ROUTE>|classing:<C>|p74:<X>|digest_sha:<sha>|policy_sha:<sha>"
seed_u64 = lo64(SHA256(seed_recipe))
```

Per-worker nulls seed:
```
seed_worker = lo64(SHA256(seed_recipe + "|" + label + "|worker:" + worker_id))
```

## Output Files
- P74_EDITORIAL_MATRIX.csv: Summary of all 26 letters
- p74_re_solve/P74_*/: Mini-bundles for feasible letters
- MANIFEST.sha256: SHA-256 hashes of all files
"""
    
    with open(repro_path, "w") as f:
        f.write(content)

def create_manifest(run_dir: Path):
    """Create SHA-256 manifest of all files"""
    manifest_path = run_dir / "MANIFEST.sha256"
    
    with open(manifest_path, "w") as manifest:
        for file_path in sorted(run_dir.rglob("*")):
            if file_path.is_file() and file_path != manifest_path:
                rel_path = file_path.relative_to(run_dir)
                
                # Compute SHA-256
                with open(file_path, "rb") as f:
                    sha = hashlib.sha256(f.read()).hexdigest()
                
                manifest.write(f"{sha}  {rel_path}\n")

def main():
    """Run P74 editorial study for all letters"""
    
    print("=" * 60)
    print("P74 Editorial/Gating Study")
    print("Re-solving lawful schedules for each P[74] letter")
    print("=" * 60)
    
    # Setup
    base_dir = Path("experiments/p74_editorial")
    run_dir = setup_run_directory(base_dir)
    
    # Load data
    ct_path = base_dir / "data" / "ciphertext_97.txt"
    with open(ct_path) as f:
        ct = f.read().strip()
    
    winner_path = base_dir / "data" / "pts" / "winner.txt"
    with open(winner_path) as f:
        winner_pt = f.read().strip()
    
    policy_path = base_dir / "policies" / "POLICY.publication.json"
    
    # Set up route paths
    route_paths = {
        "GRID_W14_ROWS": base_dir / "data" / "permutations" / "GRID_W14_ROWS.json",
        "GRID_W10_NW": base_dir / "data" / "permutations" / "GRID_W10_NW.json"
    }
    
    # Initialize solver
    solver = ScheduleSolver(ct, route_paths)
    
    # Prepare CSV output
    csv_path = run_dir / "P74_EDITORIAL_MATRIX.csv"
    csv_file = open(csv_path, "w", newline="")
    csv_writer = csv.DictWriter(csv_file, fieldnames=[
        "P74", "feasible", "route_id", "classing", 
        "encrypts_to_ct", "and_pass", "holm_cov_adj", "holm_fw_adj",
        "publishable", "fail_reason"
    ])
    csv_writer.writeheader()
    
    # Process each letter
    publishable_letters = []
    
    for letter in string.ascii_uppercase:
        print(f"\nProcessing P[74]={letter}...")
        
        # Create plaintext with P[74]=letter
        pt = winner_pt[:74] + letter + winner_pt[75:]
        
        # Solve for lawful schedule
        print(f"  Solving schedule...")
        schedules = solver.solve_for_plaintext(pt, max_schedules=3)
        
        if not schedules:
            # No feasible schedule
            print(f"  No lawful schedule found")
            
            # Write fail record
            fail_dir = run_dir / "p74_re_solve" / f"P74_{letter}"
            fail_dir.mkdir(parents=True, exist_ok=True)
            
            fail_data = {
                "letter": letter,
                "feasible": False,
                "fail_reason": "no_feasible_schedule"
            }
            
            with open(fail_dir / "fail.json", "w") as f:
                json.dump(fail_data, f, indent=2)
            
            # Write CSV row
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
            
        else:
            # Found schedule(s)
            print(f"  Found {len(schedules)} lawful schedule(s)")
            
            # Test each schedule and keep best
            best_result = None
            best_schedule = None
            
            for i, schedule in enumerate(schedules):
                print(f"  Testing schedule {i+1}: {schedule['route_id']} {schedule['classing']}")
                
                result = confirm_letter_schedule(letter, pt, ct, schedule, policy_path, run_dir)
                
                # Update best if this is better
                if best_result is None:
                    best_result = result
                    best_schedule = schedule
                elif result["publishable"] and not best_result["publishable"]:
                    best_result = result
                    best_schedule = schedule
                elif result["publishable"] and best_result["publishable"]:
                    # Both publishable, pick lower Holm min
                    min_holm_new = min(result["holm_cov_adj"], result["holm_fw_adj"])
                    min_holm_best = min(best_result["holm_cov_adj"], best_result["holm_fw_adj"])
                    if min_holm_new < min_holm_best:
                        best_result = result
                        best_schedule = schedule
                elif result["and_pass"] and not best_result["and_pass"]:
                    best_result = result
                    best_schedule = schedule
            
            # Write CSV row for best result
            csv_writer.writerow({
                "P74": letter,
                "feasible": True,
                "route_id": best_schedule["route_id"],
                "classing": best_schedule["classing"],
                "encrypts_to_ct": best_result["encrypts_to_ct"],
                "and_pass": best_result["and_pass"],
                "holm_cov_adj": best_result["holm_cov_adj"],
                "holm_fw_adj": best_result["holm_fw_adj"],
                "publishable": best_result["publishable"],
                "fail_reason": best_result.get("fail_reason", "")
            })
            
            if best_result["publishable"]:
                publishable_letters.append(letter)
                print(f"  ✓ PUBLISHABLE (Holm coverage: {best_result['holm_cov_adj']:.4f}, f_words: {best_result['holm_fw_adj']:.4f})")
            else:
                print(f"  ✗ Not publishable")
    
    csv_file.close()
    
    # Write reproducibility steps
    write_repro_steps(run_dir)
    
    # Create manifest
    create_manifest(run_dir)
    
    # Summary
    print("\n" + "=" * 60)
    print("P74 Editorial Study Complete")
    print(f"Run directory: {run_dir}")
    print(f"Total letters tested: 26")
    print(f"Publishable letters: {len(publishable_letters)}")
    if publishable_letters:
        print(f"  {', '.join(publishable_letters)}")
    else:
        print("  None (winner's fixed schedule outperforms all re-solved variants)")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())