#!/usr/bin/env python3
"""
Wrapper for real k4 confirm command with proper parameter handling.
This uses the actual k4 CLI tool for cryptographic validation.
"""

import json
import subprocess
import hashlib
from pathlib import Path
import sys

def compute_seed(route_id, classing, policy_hash, replicate=0):
    """Compute deterministic seed for nulls generation."""
    # Base recipe as per standard
    base_recipe = f"CONFIRM|K4|route:{route_id}|classing:{classing}|policy_sha:{policy_hash[:8]}"
    
    # Add replicate tag if not baseline
    if replicate > 0:
        base_recipe += f"|rep:{replicate}"
    
    # Compute seed as lower 64 bits of SHA256
    seed_bytes = hashlib.sha256(base_recipe.encode()).digest()
    seed_u64 = int.from_bytes(seed_bytes[:8], 'little') & 0xFFFFFFFFFFFFFFFF
    
    return seed_u64, base_recipe

def run_confirm_real(policy_path, pt_path, route_path, out_dir, replicate=0):
    """
    Run the real k4 confirm command with all required parameters.
    
    This executes:
    1. Rails validation (anchors, head lock, option-A)
    2. Phrase gate (Flint v2 AND Generic)
    3. 10k null hypothesis testing with Holm correction
    4. Output generation (mini-bundle)
    """
    
    # Create output directory
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    
    # Load policy to get parameters
    with open(policy_path) as f:
        policy = json.load(f)
    
    # Load route to get ID
    with open(route_path) as f:
        route_data = json.load(f)
        route_id = route_data.get("route_id", Path(route_path).stem)
    
    # Compute seed for nulls
    policy_hash = hashlib.sha256(open(policy_path, 'rb').read()).hexdigest()
    seed, seed_recipe = compute_seed(route_id, "c6a", policy_hash, replicate)
    
    # Build the actual k4 confirm command
    cmd = [
        "python3", "-m", "k4cli.cli", "confirm",
        "--ct", "experiments/0457_exec/data/ciphertext_97.txt",
        "--pt", pt_path,
        "--proof", json.dumps({
            "route_id": route_id,
            "classing": "c6a",  # Or extract from policy
            "seed": seed,
            "seed_recipe": seed_recipe
        }),
        "--perm", route_path,
        "--cuts", "experiments/0457_exec/data/canonical_cuts.json",
        "--fwords", "experiments/0457_exec/data/function_words.txt",
        "--calib", "experiments/0457_exec/data/calib_97_perplexity.json",
        "--pos-trigrams", "experiments/0457_exec/data/pos_trigrams.json",
        "--pos-threshold", "experiments/0457_exec/data/pos_threshold.txt",
        "--policy", policy_path,
        "--out", out_dir
    ]
    
    # Run the command
    print(f"Executing: k4 confirm with replicate={replicate}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        # Write error log
        error_log = Path(out_dir) / "error.log"
        with open(error_log, 'w') as f:
            f.write(f"Command: {' '.join(cmd)}\n")
            f.write(f"Return code: {result.returncode}\n")
            f.write(f"Stderr: {result.stderr}\n")
            f.write(f"Stdout: {result.stdout}\n")
        return None
    
    # Parse the coverage report
    coverage_path = Path(out_dir) / "coverage_report.json"
    if coverage_path.exists():
        with open(coverage_path) as f:
            coverage = json.load(f)
        
        # Add seed info to coverage
        coverage["seed_u64"] = seed
        coverage["seed_recipe"] = seed_recipe
        coverage["replicate"] = replicate
        
        # Write updated coverage
        with open(coverage_path, 'w') as f:
            json.dump(coverage, f, indent=2)
        
        return coverage
    
    return None

def validate_bundle(out_dir):
    """Validate that all required files are present in bundle."""
    required_files = [
        "phrase_gate_policy.json",
        "phrase_gate_report.json",
        "holm_report_canonical.json",
        "coverage_report.json",
        "near_gate_report.json"
    ]
    
    missing = []
    for file in required_files:
        if not (Path(out_dir) / file).exists():
            missing.append(file)
    
    if missing:
        print(f"Warning: Missing files in bundle: {missing}")
        return False
    
    return True

if __name__ == "__main__":
    # Test run
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", required=True)
    parser.add_argument("--pt", required=True)
    parser.add_argument("--route", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--replicate", type=int, default=0)
    
    args = parser.parse_args()
    
    result = run_confirm_real(args.policy, args.pt, args.route, args.out, args.replicate)
    
    if result:
        print(f"Success! Publishable: {result.get('nulls', {}).get('publishable', False)}")
        if validate_bundle(args.out):
            print("Bundle complete.")
    else:
        print("Failed to run confirm.")
        sys.exit(1)