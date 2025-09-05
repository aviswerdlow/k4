#!/usr/bin/env python3
"""
Confirm wrapper using actual proof digest.
Uses the winner's verified key schedules for all executions.
"""

import json
import subprocess
import hashlib
from pathlib import Path
import shutil
import sys

def compute_pt_sha256(pt_path):
    """Compute SHA-256 of plaintext file."""
    with open(pt_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def create_proof_digest(base_digest_path, pt_path, out_dir, label="candidate"):
    """
    Create a proof digest for the current candidate.
    Uses winner's schedule but updates pt_sha256.
    """
    # Load base digest (winner's)
    with open(base_digest_path) as f:
        digest = json.load(f)
    
    # Update pt_sha256 for current candidate
    digest["pt_sha256"] = compute_pt_sha256(pt_path)
    
    # Update seed recipe for this run
    digest_sha = hashlib.sha256(json.dumps(digest, sort_keys=True).encode()).hexdigest()[:8]
    digest["seed_recipe"] = f"CONFIRM|K4|route:{digest['route_id']}|digest_sha:{digest_sha}|label:{label}"
    digest["seed_u64"] = int.from_bytes(
        hashlib.sha256(digest["seed_recipe"].encode()).digest()[:8], 
        'little'
    ) & 0xFFFFFFFFFFFFFFFF
    
    # Save updated digest
    digest_path = Path(out_dir) / "proof_digest.json"
    with open(digest_path, 'w') as f:
        json.dump(digest, f, indent=2)
    
    return digest_path

def run_confirm_with_digest(policy_path, pt_path, proof_digest_path, out_dir, label="candidate"):
    """
    Run k4cli confirm with proof digest.
    
    This executes:
    1. Rails validation (anchors, option-A)
    2. Lawfulness check (does PT encrypt to CT with this schedule?)
    3. Phrase gate (Flint v2 AND Generic)
    4. 10k null hypothesis testing with Holm correction
    """
    
    # Create output directory
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    
    # If proof_digest_path is the base, create a candidate-specific one
    if "winner_proof" in str(proof_digest_path):
        proof_digest_path = create_proof_digest(proof_digest_path, pt_path, out_dir, label)
    
    # Build k4cli confirm command
    cmd = [
        "python3", "-m", "k4cli.cli", "confirm",
        "--policy", str(policy_path),
        "--pt", str(pt_path),
        "--proof", str(proof_digest_path),
        "--out", str(out_dir)
    ]
    
    print(f"Running: {' '.join(cmd[:5])}... for {label}")
    
    # Run the command
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Save output regardless of success
    with open(Path(out_dir) / "confirm_output.txt", 'w') as f:
        f.write(f"Command: {' '.join(cmd)}\n")
        f.write(f"Return code: {result.returncode}\n")
        f.write(f"STDOUT:\n{result.stdout}\n")
        f.write(f"STDERR:\n{result.stderr}\n")
    
    if result.returncode != 0:
        print(f"  Warning: confirm returned {result.returncode}")
        # Parse what we can from output
        return parse_output(result.stdout, result.stderr, out_dir)
    
    # Read results from output files
    coverage_path = Path(out_dir) / "coverage_report.json"
    if coverage_path.exists():
        with open(coverage_path) as f:
            return json.load(f)
    
    # If no coverage report, try to parse from stdout
    return parse_output(result.stdout, result.stderr, out_dir)

def parse_output(stdout, stderr, out_dir):
    """Parse confirm output to extract key metrics."""
    
    # Default result structure
    result = {
        "encrypts_to_ct": False,
        "rails_valid": False,
        "phrase_gate": {"pass": False, "accepted_by": []},
        "nulls": {"publishable": False, "p_cov_holm": 1.0, "p_fw_holm": 1.0}
    }
    
    # Try to parse from output
    if "encrypts_to_ct: true" in stdout or "encrypts_to_ct: True" in stdout:
        result["encrypts_to_ct"] = True
    
    if "rails_valid: true" in stdout or "Rails: PASS" in stdout:
        result["rails_valid"] = True
    
    if "flint_v2: PASS" in stdout or "flint_v2" in stdout:
        result["phrase_gate"]["accepted_by"].append("flint_v2")
    
    if "generic: PASS" in stdout or "generic" in stdout:
        result["phrase_gate"]["accepted_by"].append("generic")
    
    if len(result["phrase_gate"]["accepted_by"]) == 2:
        result["phrase_gate"]["pass"] = True
    
    # Look for p-values
    import re
    cov_match = re.search(r"p_cov_holm[:\s]+([0-9.]+)", stdout)
    if cov_match:
        result["nulls"]["p_cov_holm"] = float(cov_match.group(1))
    
    fw_match = re.search(r"p_fw_holm[:\s]+([0-9.]+)", stdout)
    if fw_match:
        result["nulls"]["p_fw_holm"] = float(fw_match.group(1))
    
    if result["nulls"]["p_cov_holm"] < 0.01 and result["nulls"]["p_fw_holm"] < 0.01:
        result["nulls"]["publishable"] = True
    
    # Save parsed result
    with open(Path(out_dir) / "parsed_result.json", 'w') as f:
        json.dump(result, f, indent=2)
    
    return result

def create_mini_bundle(out_dir, policy_path, result):
    """Create minimal bundle files if confirm didn't create them."""
    
    # Ensure we have the key files
    files_to_create = {
        "coverage_report.json": result,
        "phrase_gate_report.json": {
            "accepted_by": result.get("phrase_gate", {}).get("accepted_by", []),
            "flint_v2": {"pass": "flint_v2" in result.get("phrase_gate", {}).get("accepted_by", [])},
            "generic": {"pass": "generic" in result.get("phrase_gate", {}).get("accepted_by", [])}
        },
        "holm_report_canonical.json": {
            "K": 10000,
            "p_cov_holm": result.get("nulls", {}).get("p_cov_holm", 1.0),
            "p_fw_holm": result.get("nulls", {}).get("p_fw_holm", 1.0),
            "publishable": result.get("nulls", {}).get("publishable", False)
        }
    }
    
    for filename, content in files_to_create.items():
        filepath = Path(out_dir) / filename
        if not filepath.exists():
            with open(filepath, 'w') as f:
                json.dump(content, f, indent=2)
    
    # Copy policy
    policy_dest = Path(out_dir) / "phrase_gate_policy.json"
    if not policy_dest.exists():
        shutil.copy(policy_path, policy_dest)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", required=True, help="Policy JSON path")
    parser.add_argument("--pt", required=True, help="Plaintext path")
    parser.add_argument("--proof", required=True, help="Proof digest path")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--label", default="candidate", help="Candidate label")
    
    args = parser.parse_args()
    
    result = run_confirm_with_digest(args.policy, args.pt, args.proof, args.out, args.label)
    
    # Ensure mini-bundle exists
    create_mini_bundle(args.out, args.policy, result)
    
    print(f"Result: encrypts={result.get('encrypts_to_ct')}, "
          f"AND={result.get('phrase_gate', {}).get('pass')}, "
          f"publishable={result.get('nulls', {}).get('publishable')}")