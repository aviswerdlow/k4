#!/usr/bin/env python3
"""
Confirm pipeline for P74 editorial study.
For each feasible letter and schedule, run the full decision ladder:
rails → AND gate (Flint v2 + Generic) → 10k nulls
"""

import json
import hashlib
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

def compute_sha256(text: str) -> str:
    """Compute SHA-256 hash of text"""
    return hashlib.sha256(text.encode()).hexdigest()

def create_proof_digest(schedule: Dict, pt: str, ct: str, letter: str, 
                       route_path: Path, policy_path: Path) -> Dict:
    """Create proof digest for a schedule"""
    
    # Load route for SHA
    with open(route_path) as f:
        route_data = json.load(f)
    route_json = json.dumps(route_data, separators=(',', ':'))
    t2_sha = compute_sha256(route_json)
    
    # Policy SHA
    with open(policy_path) as f:
        policy_data = json.load(f)
    policy_json = json.dumps(policy_data, separators=(',', ':'))
    policy_sha = compute_sha256(policy_json)
    
    # Build forced anchor residues (from schedule if available)
    forced_anchors = []
    # This would be populated from the schedule solver's detailed output
    
    # Build seed recipe
    classing = schedule["classing"]
    route_id = schedule["route_id"]
    digest_str = f"{route_id}|{classing}|p74:{letter}"
    digest_sha = compute_sha256(digest_str)[:8]
    
    seed_recipe = f"CONFIRM|K4|route:{route_id}|classing:{classing}|p74:{letter}|digest_sha:{digest_sha}|policy_sha:{policy_sha[:8]}"
    seed_u64 = int(hashlib.sha256(seed_recipe.encode()).hexdigest()[:16], 16)
    
    return {
        "ct_sha256": compute_sha256(ct),
        "pt_sha256": compute_sha256(pt),
        "route_id": route_id,
        "t2_path": f"permutations/{route_id}.json",
        "t2_sha256": t2_sha,
        "classing": classing,
        "per_class": schedule["per_class"],
        "anchor_policy": "Option-A",
        "anchors_0idx": {
            "EAST": [21, 24],
            "NORTHEAST": [25, 33],
            "BERLINCLOCK": [63, 73]
        },
        "forced_anchor_residues": forced_anchors,
        "seed_recipe": seed_recipe,
        "seed_u64": seed_u64,
        "lm_manifest_sha256": "lane_pinned_manifest"
    }

def run_k4cli_confirm(policy_path: Path, pt_path: Path, ct_path: Path, 
                     proof_path: Path, out_dir: Path) -> Dict:
    """Run k4cli confirm command"""
    
    cmd = [
        "python3", "-m", "k4cli.cli", "confirm",
        "--policy", str(policy_path),
        "--pt", str(pt_path),
        "--ct", str(ct_path),
        "--proof", str(proof_path),
        "--out", str(out_dir)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Command timed out after 300 seconds",
            "returncode": -1
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }

def create_fallback_reports(pt: str, ct: str, schedule: Dict, letter: str, 
                           out_dir: Path, policy_path: Path) -> Dict:
    """Create fallback reports when k4cli fails"""
    
    # Create minimal coverage report
    coverage = {
        "rails": {
            "anchors_0idx": {
                "EAST": [21, 24],
                "NORTHEAST": [25, 33],
                "BERLINCLOCK": [63, 73]
            },
            "head_lock": [0, 74],
            "tail_guard": None,
            "na_only": True,
            "option_A": True
        },
        "pt_sha256": compute_sha256(pt),
        "ct_sha256": compute_sha256(ct),
        "route_id": schedule["route_id"],
        "t2_sha256": "pending_calculation",
        "encrypts_to_ct": schedule.get("encrypts_to_ct", False),
        "seed_recipe": f"CONFIRM|K4|p74:{letter}",
        "seed_u64": 1337,
        "near_gate": {
            "coverage": 0.0,
            "f_words": 0.0,
            "has_verb": False,
            "pass": False
        },
        "phrase_gate": {
            "accepted_by": [],
            "pass": False
        },
        "nulls": {
            "status": "not_run",
            "K": 10000,
            "holm_adj_p": {
                "coverage": 1.0,
                "f_words": 1.0
            }
        }
    }
    
    with open(out_dir / "coverage_report.json", "w") as f:
        json.dump(coverage, f, indent=2)
    
    # Create minimal phrase gate report
    phrase_report = {
        "flint_v2": {
            "status": "not_evaluated",
            "pass": False
        },
        "generic": {
            "status": "not_evaluated",
            "pass": False
        },
        "accepted_by": [],
        "pass": False
    }
    
    with open(out_dir / "phrase_gate_report.json", "w") as f:
        json.dump(phrase_report, f, indent=2)
    
    # Create minimal holm report
    holm_report = {
        "K": 10000,
        "metrics": {
            "coverage": {
                "p_raw": 1.0,
                "p_holm": 1.0
            },
            "f_words": {
                "p_raw": 1.0,
                "p_holm": 1.0
            }
        },
        "publishable": False
    }
    
    with open(out_dir / "holm_report_canonical.json", "w") as f:
        json.dump(holm_report, f, indent=2)
    
    # Copy policy
    shutil.copy(policy_path, out_dir / "phrase_gate_policy.json")
    
    # Create hashes file
    with open(out_dir / "hashes.txt", "w") as f:
        f.write(f"pt_sha256: {compute_sha256(pt)}\n")
        f.write(f"ct_sha256: {compute_sha256(ct)}\n")
        f.write(f"route: {schedule['route_id']}\n")
        f.write(f"p74: {letter}\n")
    
    return {
        "encrypts_to_ct": schedule.get("encrypts_to_ct", False),
        "and_pass": False,
        "holm_cov_adj": 1.0,
        "holm_fw_adj": 1.0,
        "publishable": False,
        "fail_reason": "k4cli_not_available"
    }

def confirm_letter_schedule(letter: str, pt: str, ct: str, schedule: Dict,
                           policy_path: Path, run_dir: Path) -> Dict:
    """Run full confirm pipeline for a letter with its schedule"""
    
    # Create output directory
    letter_dir = run_dir / f"p74_re_solve" / f"P74_{letter}"
    letter_dir.mkdir(parents=True, exist_ok=True)
    
    # Write plaintext
    pt_path = letter_dir / "plaintext_97.txt"
    with open(pt_path, "w") as f:
        f.write(pt)
    
    # Write ciphertext
    ct_path = letter_dir / "ciphertext_97.txt"
    with open(ct_path, "w") as f:
        f.write(ct)
    
    # Find route path
    route_path = Path(f"experiments/p74_editorial/data/permutations/{schedule['route_id']}.json")
    
    # Create proof digest
    proof = create_proof_digest(schedule, pt, ct, letter, route_path, policy_path)
    proof_path = letter_dir / "proof_digest.json"
    with open(proof_path, "w") as f:
        json.dump(proof, f, indent=2)
    
    # Try to run k4cli confirm
    result = run_k4cli_confirm(policy_path, pt_path, ct_path, proof_path, letter_dir)
    
    if result["success"]:
        # Parse k4cli output
        try:
            # Load generated reports
            coverage_report = json.load(open(letter_dir / "coverage_report.json"))
            phrase_report = json.load(open(letter_dir / "phrase_gate_report.json"))
            holm_report = json.load(open(letter_dir / "holm_report_canonical.json"))
            
            return {
                "encrypts_to_ct": coverage_report.get("encrypts_to_ct", False),
                "and_pass": phrase_report.get("pass", False),
                "holm_cov_adj": holm_report["metrics"]["coverage"]["p_holm"],
                "holm_fw_adj": holm_report["metrics"]["f_words"]["p_holm"],
                "publishable": (
                    holm_report["metrics"]["coverage"]["p_holm"] < 0.01 and
                    holm_report["metrics"]["f_words"]["p_holm"] < 0.01
                ),
                "fail_reason": None if phrase_report.get("pass") else "phrase_gate_fail"
            }
        except Exception as e:
            # k4cli ran but output parsing failed
            return create_fallback_reports(pt, ct, schedule, letter, letter_dir, policy_path)
    else:
        # k4cli failed, create fallback reports
        return create_fallback_reports(pt, ct, schedule, letter, letter_dir, policy_path)


def main():
    """Test confirm pipeline"""
    import sys
    from solve_schedule import ScheduleSolver
    
    # Test letter
    letter = sys.argv[1].upper() if len(sys.argv) > 1 else "T"
    
    # Load data
    ct_path = Path("experiments/p74_editorial/data/ciphertext_97.txt")
    with open(ct_path) as f:
        ct = f.read().strip()
    
    winner_path = Path("experiments/p74_editorial/data/pts/winner.txt")
    with open(winner_path) as f:
        winner_pt = f.read().strip()
    
    # Create test plaintext
    pt = winner_pt[:74] + letter + winner_pt[75:]
    
    # Get schedule
    route_paths = {
        "GRID_W14_ROWS": Path("experiments/p74_editorial/data/permutations/GRID_W14_ROWS.json"),
        "GRID_W10_NW": Path("experiments/p74_editorial/data/permutations/GRID_W10_NW.json")
    }
    
    solver = ScheduleSolver(ct, route_paths)
    schedules = solver.solve_for_plaintext(pt, max_schedules=1)
    
    if not schedules:
        print(f"No lawful schedule found for P[74]={letter}")
        return 1
    
    # Run confirm
    policy_path = Path("experiments/p74_editorial/policies/POLICY.publication.json")
    run_dir = Path(f"experiments/p74_editorial/runs/{datetime.now().strftime('%Y%m%d')}")
    
    result = confirm_letter_schedule(letter, pt, ct, schedules[0], policy_path, run_dir)
    
    print(f"Results for P[74]={letter}:")
    print(f"  Encrypts to CT: {result['encrypts_to_ct']}")
    print(f"  AND gate pass: {result['and_pass']}")
    print(f"  Holm coverage adj-p: {result['holm_cov_adj']:.4f}")
    print(f"  Holm f_words adj-p: {result['holm_fw_adj']:.4f}")
    print(f"  Publishable: {result['publishable']}")
    if result['fail_reason']:
        print(f"  Fail reason: {result['fail_reason']}")
    
    return 0


if __name__ == "__main__":
    exit(main())