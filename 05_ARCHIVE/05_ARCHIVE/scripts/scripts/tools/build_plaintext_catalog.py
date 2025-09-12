#!/usr/bin/env python3
"""Build a catalog of all plaintexts from v4.1.1 K=200 run.

For each candidate, runs feasibility check and captures full 97-char plaintext if lawful.
"""

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def sha256_file(filepath):
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def build_plaintext_from_head(head_pre, head_post):
    """Build 97-char plaintext from head window."""
    # Head is 0:74, need to add tail 74:97
    head = head_pre + head_post  # This gives us 0:74
    
    # For v4.1.1, we need to generate the tail deterministically
    # Using a simple pattern for now (can be replaced with actual generator)
    tail = "ETHATBETHEMTHEFOLLOWWI"  # Example tail to reach 97 chars
    
    full_plaintext = head + tail
    return full_plaintext[:97]  # Ensure exactly 97 chars


def run_feasibility(label, explore_matrix_row, work_dir):
    """Run feasibility check for a candidate.
    
    Returns dict with results including plaintext if lawful.
    """
    work_path = Path(work_dir)
    work_path.mkdir(parents=True, exist_ok=True)
    
    # Check if already processed
    proof_path = work_path / "proof_digest.json"
    plaintext_path = work_path / "plaintext_97.txt"
    
    if proof_path.exists() and plaintext_path.exists():
        with open(proof_path) as f:
            proof = json.load(f)
        
        plaintext = plaintext_path.read_text().strip()
        
        if proof.get("encrypts_to_ct", False):
            # Already lawful, read plaintext
            pt_sha = sha256_file(plaintext_path)
            return {
                "encrypts_to_ct": True,
                "plaintext_97": plaintext,
                "pt_sha256": pt_sha,
                "route_id": proof.get("route_id", ""),
                "t2_sha256": proof.get("t2_sha256", ""),
                "classing": proof.get("classing", ""),
                "notes": ""
            }
        else:
            # Already failed
            return {
                "encrypts_to_ct": False,
                "plaintext_97": "",
                "pt_sha256": "",
                "route_id": proof.get("route_id", ""),
                "t2_sha256": "",
                "classing": proof.get("classing", ""),
                "notes": proof.get("notes", "no feasible schedule")
            }
    
    # Need to run feasibility
    print(f"  Running feasibility for {label}...")
    
    # Build plaintext from head window
    head_pre = explore_matrix_row.get("head_pre", "")
    head_post = explore_matrix_row.get("head_post", "")
    seed = explore_matrix_row.get("seed_u64", "")
    
    # Try GRID routes in order
    routes = ["GRID_W14_ROWS", "GRID_W14_BOU", "GRID_W14_NE", "GRID_W14_NW",
              "GRID_W12_ROWS", "GRID_W12_BOU", "GRID_W10_ROWS", "GRID_W10_NW"]
    
    for route in routes:
        cmd = [
            "python3",
            "experiments/pipeline_v4/scripts/run_confirm_gates.py",
            "--label", label,
            "--seed", str(seed),
            "--head-pre", head_pre,
            "--head-post", head_post,
            "--route", route,
            "--mode", "feasibility-only",
            "--out", str(work_path),
            "--max-budget", "50000"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Check if lawful
            if proof_path.exists():
                with open(proof_path) as f:
                    proof = json.load(f)
                
                if proof.get("encrypts_to_ct"):
                    # Success! Read plaintext
                    if plaintext_path.exists():
                        plaintext = plaintext_path.read_text().strip()
                        pt_sha = sha256_file(plaintext_path)
                        return {
                            "encrypts_to_ct": True,
                            "plaintext_97": plaintext,
                            "pt_sha256": pt_sha,
                            "route_id": route,
                            "t2_sha256": proof["t2_sha256"],
                            "classing": proof["classing"],
                            "notes": ""
                        }
                    
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            print(f"    Route {route} failed: {e}")
            continue
    
    # All routes failed
    return {
        "encrypts_to_ct": False,
        "plaintext_97": "",
        "pt_sha256": "",
        "route_id": "",
        "t2_sha256": "",
        "classing": "",
        "notes": "no feasible schedule found"
    }


def load_explore_matrix(matrix_path):
    """Load explore matrix as dict keyed by label."""
    matrix = {}
    with open(matrix_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            matrix[row["label"]] = row
    return matrix


def main():
    """Build plaintext catalog for all candidates."""
    
    # Paths
    base_dir = Path("experiments/pipeline_v4/runs/v4_1_1/k200")
    matrix_path = base_dir / "explore_matrix.csv"
    queue_path = base_dir / "promotion_queue.json"
    catalog_path = base_dir / "PLAINTEXT_CATALOG.csv"
    work_base = Path("runs/confirm/catalog")
    
    # Load candidates
    print("Loading candidates...")
    if queue_path.exists():
        with open(queue_path) as f:
            queue = json.load(f)
        candidates = [c["label"] for c in queue["candidates"]]
        print(f"  Loaded {len(candidates)} candidates from promotion queue")
    else:
        # Fall back to explore matrix
        matrix = load_explore_matrix(matrix_path)
        candidates = list(matrix.keys())
        print(f"  Loaded {len(candidates)} candidates from explore matrix")
    
    # Load explore matrix for metrics
    matrix = load_explore_matrix(matrix_path)
    
    # Process each candidate
    results = []
    for i, label in enumerate(candidates, 1):
        print(f"\n[{i}/{len(candidates)}] Processing {label}")
        
        # Get explore metrics
        explore_row = matrix.get(label, {})
        
        # Run feasibility
        work_dir = work_base / label
        feasibility = run_feasibility(label, explore_row, work_dir)
        
        # Build catalog row
        row = {
            "label": label,
            "seed_u64": explore_row.get("seed_u64", ""),
            "weights_sha256": explore_row.get("weights_sha256", "d2b426b77c965c3ecd804c8d25c48ab45f0635db18275f68827cd48fa0d98be0"),
            "route_id": feasibility["route_id"],
            "t2_sha256": feasibility["t2_sha256"],
            "classing": feasibility["classing"],
            "encrypts_to_ct": str(feasibility["encrypts_to_ct"]).lower(),
            "plaintext_97": feasibility["plaintext_97"],
            "pt_sha256": feasibility["pt_sha256"],
            "coverage": explore_row.get("cov_post", ""),
            "f_words": explore_row.get("fw_post", ""),
            "has_verb": explore_row.get("verb_post", ""),
            "delta_windowed": explore_row.get("delta_windowed", ""),
            "delta_shuffled": explore_row.get("delta_shuffled", ""),
            "leakage_diff": explore_row.get("leakage_diff", "0.000"),
            "notes": feasibility["notes"]
        }
        results.append(row)
        
        # Progress
        if feasibility["encrypts_to_ct"]:
            print(f"  ✅ Lawful on {feasibility['route_id']}")
        else:
            print(f"  ❌ Not lawful: {feasibility['notes']}")
    
    # Write catalog
    print(f"\nWriting catalog to {catalog_path}")
    with open(catalog_path, 'w', newline='') as f:
        fieldnames = [
            "label", "seed_u64", "weights_sha256", "route_id", "t2_sha256",
            "classing", "encrypts_to_ct", "plaintext_97", "pt_sha256",
            "coverage", "f_words", "has_verb", "delta_windowed",
            "delta_shuffled", "leakage_diff", "notes"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # Summary
    lawful_count = sum(1 for r in results if r["encrypts_to_ct"] == "true")
    print(f"\n✅ Complete!")
    print(f"  Total candidates: {len(results)}")
    print(f"  Lawful (encrypts_to_ct): {lawful_count}")
    print(f"  Failed: {len(results) - lawful_count}")
    print(f"  Catalog: {catalog_path}")


if __name__ == "__main__":
    main()